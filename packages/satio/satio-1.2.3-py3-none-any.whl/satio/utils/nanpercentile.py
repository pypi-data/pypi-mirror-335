import numpy as np
from numba import njit, float32, int64
from functools import wraps
from time import time


@njit(float32(float32[float32], int64))
def _nanpercentile(arr, percent):
    """
    Find the percentile of a 1d array containing nans.
    """
    # if np.all(np.isnan(arr)):
    #     return np.nan

    ratio = percent / 100
    arr = np.sort(arr[~np.isnan(arr)])
    if not arr.size:
        return np.nan
    k = (arr.shape[0] - 1) * ratio
    f = np.floor(k)
    c = np.ceil(k)

    if f == c:
        return arr[int(k)]

    else:
        d0 = arr[int(f)] * (c-k)
        d1 = arr[int(c)] * (k-f)
    arr = None
    return d0 + d1


@njit(float32[:, :](float32[:, :, :], int64))
def hyper_nanpercentile_flat(arr, percent):
    """
    Returns the nth percentile of a time cube array with shape
    (bands, layers, rows * cols). Each layer is a satellite acquisition and the
    nanpercentile is computed along axis 0.
    The axis parameters is useless, it only allows backwards compatibility
    with np.nanpercentilefor this particular case.
    """
    bands, _, rows = arr.shape
    percentile = np.zeros((bands, rows), dtype=np.float32)
    percentile[...] = np.nan
    for b in range(bands):
        for r in range(rows):
            percentile[b, r] = _nanpercentile(arr[b, :, r], percent)
    arr = None
    return percentile


@njit(float32[:, :, :](float32[:, :, :, :], int64))
def hyper_nanpercentile(arr, percent):
    """
    Returns the nth percentile of a time cube array with shape
    (layers, rows, cols). Each layer is a satellite acquisition and the
    nanpercentile is computed along axis 0.
    The axis parameters is useless, it only allows backwards compatibility
    with np.nanpercentile for this particular case.
    """
    bands, _, rows, cols = arr.shape
    percentile = np.zeros((bands, rows, cols), dtype=np.float32)
    percentile[...] = np.nan
    for b in range(bands):
        for r in range(rows):
            for c in range(cols):
                percentile[b, r, c] = _nanpercentile(arr[b, :, r, c], percent)
    arr = None
    return percentile


@njit(float32[:, :](float32[:, :, :], int64))
def nanpercentile(arr, percent):
    """
    Returns the nth percentile of a time cube array with shape
    (layers, rows, cols). Each layer is a satellite acquisition and the
    nanpercentile is computed along axis 0.
    The axis parameters is useless, it only allows backwards compatibility
    with np.nanpercentilefor this particular case.
    """
    _, rows, cols = arr.shape
    percentile = np.zeros((rows, cols), dtype=np.float32)
    percentile[...] = np.nan
    for r in range(rows):
        for c in range(cols):
            percentile[r, c] = _nanpercentile(arr[:, r, c], percent)

    arr = None
    return percentile


@njit
def create_test_array(test_shape, nans_ratio=0.2):
    test_arr = np.random.rand(*test_shape)
    for i in range(test_shape[1]):
        for j in range(test_shape[2]):
            test_arr[:, i, j] = (test_arr[:, i, j] * np.random.rand()
                                 * np.random.randint(2, 5))
    test_arr_v = test_arr.reshape(-1)
    flag = np.random.rand(test_arr_v.shape[0]) <= nans_ratio
    test_arr_v[flag] = np.nan
    test_arr_nan = test_arr_v.reshape(test_arr.shape)
    return test_arr, test_arr_nan


def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        print('Elapsed time: {:.1f} seconds.'.format(end-start))
        return result
    return wrapper


if __name__ == '__main__':

    percent = 50
    test_shape = (108, 1000, 1000)
    test_arr, test_arr_nan = create_test_array(test_shape, nans_ratio=0.2)

    print("Percentile performance test on array of shape {}"
          .format(test_shape))

    @timing
    def test1():
        print("\nNormal numpy np.percentile:")
        return np.percentile(test_arr, percent, axis=0)

    @timing
    def test2():
        print("\nNumba nanpercentile implementation:")
        return nanpercentile(test_arr_nan, percent, axis=0)

    @timing
    def test3():
        print("\nNumpy np.nanpercentile:")
        return np.nanpercentile(test_arr_nan, percent, axis=0)

    p1, p2, p3 = test1(), test2(), test3()
    comparison = np.all(p2 == p3)
    print("Results comparison:",
          "Are Numba implementation and np.nanpercentile equal?\n",
          comparison)
