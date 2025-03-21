import numpy as np
from scipy import ndimage


def mtfilter(stack, kernel, mtwin=7, enl=3):
    """
    stack: np array with multi-temporal stack of backscatter images (linear
    scale)

    kernel: 'mean','gauss','gamma' - 'gamma' is recommended (slower than the
    other kernels though)

    mtwin: filter window size - recommended mtwin=7

    enl: only required for kernel 'gamma' - recommended for S1 enl = 3
    """
    rows, cols, layers = stack.shape
    filtim = np.zeros((rows, cols, layers))

    rcs = image_sum = image_num = image_fil = None  # pylance unbound warning

    for no in range(0, layers):
        # Initiate arrays
        if no == 0:
            image_sum = np.zeros((rows, cols))
            image_num = np.zeros((rows, cols))
            image_fil = np.zeros((rows, cols, layers))

        if kernel == 'mean':
            rcs = ndimage.uniform_filter(
                stack[:, :, no], size=mtwin, mode='mirror')
        elif kernel == 'gauss':
            rcs = ndimage.gaussian_filter(
                stack[:, :, no], mtwin / 4, mode='mirror')
        elif kernel == 'gamma':
            rcs = GammaMAP(stack[:, :, no], mtwin, enl, 0)

        with np.errstate(divide='ignore', invalid='ignore'):
            ratio = (stack[:, :, no] / rcs)
            ratio[np.isnan(ratio)] = 0

        image_sum = image_sum+ratio
        image_num = image_num+(ratio > 0)
        image_fil[:, :, no] = rcs

    with np.errstate(invalid='ignore'):
        for no in range(0, layers):
            im = stack[:, :, no]
            filtim1 = image_fil[:, :, no]*image_sum/image_num
            filtim1[np.isnan(filtim1)] = 0
            fillmask = (filtim1 == 0) & (im > 0)
            filtim1[fillmask] = im[fillmask]
            mask = im > 0
            filtim1[mask == 0] = im[mask == 0]
            filtim[:, :, no] = filtim1

    return filtim


def GammaMAP(band, size, ENL, ndv):
    img = band
    img[band == ndv] = 0.
    sig_v2 = 1.0 / ENL
    ENL2 = ENL + 1.
    sfak = 1.0 + sig_v2
    img_mean2 = ndimage.uniform_filter(pow(img, 2), size=size)
    img_mean2[img == ndv] = 0.
    img_mean = ndimage.uniform_filter(img, size=size)
    img_mean[img == ndv] = 0.
    var_z = img_mean2 - pow(img_mean, 2)
    out = img_mean

    with np.errstate(divide='ignore', invalid='ignore'):
        fact1 = var_z / pow(img_mean, 2)
        fact1[np.isnan(fact1)] = 0

        mask = (fact1 > sig_v2) & ((var_z - pow(img_mean, 2) * sig_v2) > 0.)

        if mask.any():
            n = (pow(img_mean, 2) * sfak) / (var_z - pow(img_mean, 2) * sig_v2)
            phalf = (img_mean * (ENL2 - n)) / (2 * n)
            q = ENL * img_mean * img / n
            out[mask] = -phalf[mask] + np.sqrt(pow(phalf[mask], 2) + q[mask])

    out[img == 0.] = ndv
    return out
