import numpy as np
from loguru import logger
import time
from numba import (njit, float32, uint8, uint16,
                   int32, uint32, boolean, types)


@njit(types.UniTuple(int32, 2)(uint16, float32))
def offset(length, angle):
    """Return the offset in pixels for a given length and angle"""
    dv = np.array([length * np.sign(-np.sin(angle))]).astype(np.int32)
    dh = np.array([length * np.sign(np.cos(angle))]).astype(np.int32)
    return (dv[0], dh[0])


@njit(uint32[:, :](uint32[:, :], uint16, uint16,
                   uint8))
def crop(img, crow, ccol, win):
    """Return a square crop of img centered at center
    (side = 2*win + 1)"""
    side = 2*win + 1
    return img[crow - win: crow - win + side,
               ccol - win: ccol - win + side]


@njit(uint32[:, :](uint32[:, :], uint32[:, :], uint16))
def encode_cooccurrence(x, y, levels):
    """Return the code corresponding to co-occurrence
    of intensities x and y"""
    return x*levels + y


@njit(uint32[:, :, :, :](uint32[:, :], uint16, uint16, uint8,
                         uint16[:], float32[:], uint16))
def cooc_maps(img, crow, ccol, win,
              d, theta, levels):
    """
    Return a set of co-occurrence maps for different
    d and theta in a square
    crop centered at center (side = 2*w + 1)
    """
    shape = (2*win + 1, 2*win + 1, d.shape[0], theta.shape[0])
    cooc = np.zeros(shape=shape, dtype=np.uint32)
    Ii = crop(img, crow, ccol, win)
    for d_index, length in enumerate(d):
        for a_index, angle in enumerate(theta):
            (dv, dh) = offset(length, angle)
            Ij = crop(img, crow + dv, ccol + dh, win)
            cooc[:, :, d_index, a_index] = encode_cooccurrence(
                Ii, Ij, levels)
    return cooc


@njit(types.UniTuple(uint32[:], 2)(uint32[:], uint16))
def decode_cooccurrence(code, levels):
    """Return the intensities x, y corresponding to code"""
    return (code//levels, np.mod(code, levels))


@njit(float32[:, :, :, :](uint32[:, :, :, :], uint16))
def compute_glcms(cooccurrence_maps, levels):
    """Compute the cooccurrence frequencies of the
    cooccurrence maps"""
    Nr, Na = cooccurrence_maps.shape[2:]
    glcms = np.zeros(shape=(levels, levels, Nr, Na),
                     dtype=np.float32)
    for r in range(Nr):
        for a in range(Na):
            codes = np.unique(cooccurrence_maps[:, :, r, a])
            freqs = np.zeros_like(codes, dtype=np.float32)
            for c in range(codes.shape[0]):
                freqs[c] = np.count_nonzero(
                    cooccurrence_maps[:, :, r, a] == codes[c])
            freqs = freqs / freqs.sum()
            (i, j) = decode_cooccurrence(codes, levels=levels)
            for o in range(i.shape[0]):
                glcms[i[o], j[o], r, a] = freqs[o]
    return glcms


@njit(float32[:, :, :](float32[:, :, :, :]))
def greycoprops(P):
    """Calculate texture properties of a GLCM.

    Compute a feature of a grey level co-occurrence matrix to serve as
    a compact summary of the matrix.
    Each GLCM is normalized to have a sum of 1 before the computation
    of texture properties.

    Parameters
    ----------
    P : ndarray
        Input array. `P` is the grey-level co-occurrence histogram
        for which to compute the specified property. The value
        `P[i,j,d,theta]` is the number of times that grey-level j
        occurs at a distance d and at an angle theta from
        grey-level i.
    prop : {0: 'contrast',
            1: 'dissimilarity',
            2: 'homogeneity',
            3: 'energy',
            4: 'correlation',
            5:'ASM'}
        The property of the GLCM to compute.

    References
    ----------
    .. [1] The GLCM Tutorial Home Page,
           http://www.fp.ucalgary.ca/mhallbey/tutorial.htm

    """
    # preparations
    (num_level, num_level2, num_dist, num_angle) = P.shape
    results = np.empty((6, num_dist, num_angle),
                       dtype=np.float32)
    ar = np.arange(num_level, dtype=np.float32)
    i = np.empty((num_level, 1), dtype=np.float32)
    j = np.empty((1, num_level), dtype=np.float32)
    i[:, 0] = ar
    j[0, :] = ar
    weights = np.empty((3, num_level, num_level),
                       dtype=np.float32)
    weights[0, :, :] = (i - j) ** 2
    weights[1, :, :] = np.abs(i - j)
    weights[2, :, :] = 1 / (1 + (i - j) ** 2)

    # compute all metrics
    for d in range(num_dist):
        for a in range(num_angle):
            # normalize GLCM
            glcm_sums = np.sum(P[:, :, d, a])
            if np.equal(glcm_sums, 0.):
                glcm_sums = 1
            P2 = P[:, :, d, a] / glcm_sums

            # contrast
            results[0, d, a] = np.sum(P2 * weights[0, :, :])

            # dissimilarity
            results[1, d, a] = np.sum(P2 * weights[1, :, :])

            # homogeneity
            results[2, d, a] = np.sum(P2 * weights[2, :, :])

            # ASM
            results[3, d, a] = np.sum(P2 ** 2)

            # correlation
            diff_i = i - np.sum(i * P2)
            diff_j = j - np.sum(j * P2)
            std_i = np.sqrt(np.sum(P2 * (diff_i) ** 2))
            std_j = np.sqrt(np.sum(P2 * (diff_j) ** 2))
            cov = np.sum(P2 * (diff_i * diff_j))
            if np.logical_or(np.less(std_i, 1e-15),
                             np.less(std_j, 1e-15)):
                results[4, d, a] = 1
            else:
                results[4, d, a] = cov / (std_i * std_j)

            # energy
            results[5, d, a] = np.sqrt(results[3, d, a])

    return results


@njit(float32[:](float32[:, :, :, :], uint8[:], boolean))
def compute_props(glcms, props, avg):
    """Return a feature vector corresponding to a set of GLCM"""
    Nr, Na = glcms.shape[2:]
    # compute all properties
    featuresAll = greycoprops(glcms)
    # select the ones you need
    featuresSel = featuresAll[props, ...]
    if avg:
        features = np.empty((len(props)), dtype=np.float32)
        for i in range(len(props)):
            features[i] = np.mean(featuresSel[i, :, :])
    else:
        features = np.empty((Nr * Na * len(props)),
                            dtype=np.float32)
        featuresSel = featuresSel.transpose(1, 2, 0)
        count = 0
        for r in range(Nr):
            for a in range(Na):
                for p in range(len(props)):
                    features[count] = featuresSel[r, a, p]
                    count += 1
    return features


@njit(float32[:, :, :](uint32[:, :], uint16, uint16,
                       uint8, uint8, uint8,
                       uint16[:], float32[:],
                       uint16, uint8[:], boolean))
def haralick_pixel_wrapper(arr, rows, cols, n_text_feat,
                           margin, win, d, theta, levels,
                           metrics, avg):

    feature_map = np.zeros(shape=(rows, cols, n_text_feat),
                           dtype=np.float32)
    for m in range(rows):
        for n in range(cols):
            crow = m + margin
            ccol = n + margin
            coocs = cooc_maps(arr, crow, ccol,
                              win, d, theta, levels)
            glcms = compute_glcms(coocs, levels)
            feature_map[m, n, :] = compute_props(glcms, metrics, avg)

    return feature_map.transpose(2, 0, 1)


def haralick_features(img, feat_name, win, d, theta,
                      levels, metrics, avg):
    """
    Returns a set of Haralick texture features for the input feature
    :param img -> 2D input array (only 1 feature allowed as input!)
    :param feat_name -> name of the input feature
    :param win -> spatial window included when calculating texture
    for given pixel
        The window is defined as (2*win + 1)
        -> win=2 means a 5x5 pixel window!
    :param d -> list of pixel distances to be used for texture calc
    :param theta -> list of pixel angles to be used for texture calc
    :param levels -> number of levels to be considered during
        texture calc
    :param metrics -> list of metrics to be computed. Possible options:
        contrast
        dissimilarity
        homogeneity
        energy
        correlation
        ASM
    :param avg (boolean) -> whether or not to compute the
        average texture feature over all considered pixel
        distances and angles

    ! The execution of this function may take a while, depending
    on the settings. If quick estimate is desired, choose only one
    d and one theta, set the levels to a small number (e.g. 50) and
    use avg=True
    """
    # convert metrics to int representation
    conv_metrics = {'contrast': 0,
                    'dissimilarity': 1,
                    'homogeneity': 2,
                    'energy': 3,
                    'correlation': 4,
                    'ASM': 5}
    for met in metrics:
        if met not in conv_metrics.keys():
            raise ValueError(f'{met} not supported as texture'
                             'metric.')
    metrics_num = np.array([conv_metrics[m] for m in metrics],
                           dtype=np.uint8)
    # padding input image
    rows, cols = img.shape
    margin = win + max(d)
    arr = np.pad(img, margin, mode='reflect')
    # create texture feature names
    feat_name_ls = feat_name.split('-')
    feat_name_new = ''.join(feat_name_ls[0:2])
    res = feat_name_ls[-1]
    if avg:
        n_text_feat = len(metrics)
        text_feat_names = [f'{feat_name_new}-tx_{p[0:3]}-{res}'
                           for p in metrics]
    else:
        n_text_feat = len(d) * len(theta) * len(metrics)
        text_feat_names = []
        for r in d:
            for t in theta:
                for p in metrics:
                    text_feat_names.append(
                        f'{feat_name_new}-tx_{p[0:3]}_'
                        f'{str(r)}_{str(int(t * 180 / np.pi))}-{res}')

    # convert lists to arrays
    theta = np.array(theta, dtype=np.float32)
    d = np.array(d, dtype=np.uint16)
    # compute desired features for each pixel
    feature_map = haralick_pixel_wrapper(arr,
                                         rows,
                                         cols,
                                         n_text_feat,
                                         margin,
                                         win,
                                         d,
                                         theta,
                                         levels,
                                         metrics_num,
                                         avg)
    return feature_map, text_feat_names
