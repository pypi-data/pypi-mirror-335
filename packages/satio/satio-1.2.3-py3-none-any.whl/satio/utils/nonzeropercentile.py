import numpy as np
from numba import njit, uint16, int64


@njit(uint16(uint16[:], int64))
def _nonzeropercentile(arr, percent):
    """
    Find the percentile of a 1d array containing nans.
    """
    # if np.all(np.isnan(arr)):
    #     return np.nan

    ratio = percent / 100
    arr = np.sort(arr[arr != 0])

    if not arr.size:
        return uint16(0)
    k = (arr.shape[0] - 1) * ratio
    f = np.floor(k)
    c = np.ceil(k)

    if f == c:
        return uint16(arr[int(k)])

    else:
        d0 = uint16(arr[int(f)] * (c-k))
        d1 = uint16(arr[int(c)] * (k-f))
    arr = None
    return d0 + d1


@njit(uint16[:, :](uint16[:, :, :], int64))
def hyper_nonzeropercentile_flat(arr, percent):
    """
    Returns the nth percentile of a time cube array with shape
    (bands, layers, rows * cols). Each layer is a satellite acquisition and the
    nonzeropercentile is computed along axis 0.
    The axis parameters is useless, it only allows backwards compatibility
    with np.nonzeropercentilefor this particular case.
    """
    bands, _, rows = arr.shape
    percentile = np.zeros((bands, rows), dtype=np.uint16)
    percentile[...] = 0
    for b in range(bands):
        for r in range(rows):
            percentile[b, r] = _nonzeropercentile(arr[b, :, r], percent)
    arr = None
    return percentile


@njit(uint16[:, :, :](uint16[:, :, :, :], int64))
def hyper_nonzeropercentile(arr, percent):
    """
    Returns the nth percentile of a time cube array with shape
    (layers, rows, cols). Each layer is a satellite acquisition and the
    nonzeropercentile is computed along axis 0.
    The axis parameters is useless, it only allows backwards compatibility
    with np.nonzeropercentile for this particular case.
    """
    bands, _, rows, cols = arr.shape
    percentile = np.zeros((bands, rows, cols), dtype=np.uint16)
    percentile[...] = 0
    for b in range(bands):
        for r in range(rows):
            for c in range(cols):
                percentile[b, r, c] = _nonzeropercentile(
                    arr[b, :, r, c], percent)
    arr = None
    return percentile


@njit(uint16[:, :](uint16[:, :, :], int64))
def nonzeropercentile(arr, percent):
    """
    Returns the nth percentile of a time cube array with shape
    (layers, rows, cols). Each layer is a satellite acquisition and the
    nonzeropercentile is computed along axis 0.
    The axis parameters is useless, it only allows backwards compatibility
    with np.nonzeropercentilefor this particular case.
    """
    _, rows, cols = arr.shape
    percentile = np.zeros((rows, cols), dtype=np.uint16)
    percentile[...] = uint16(0)
    for r in range(rows):
        for c in range(cols):
            percentile[r, c] = _nonzeropercentile(arr[:, r, c], percent)

    arr = None
    return percentile
