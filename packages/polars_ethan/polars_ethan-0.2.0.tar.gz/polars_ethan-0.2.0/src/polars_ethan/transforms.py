from numba import float64, guvectorize
import numpy as np

@guvectorize([(float64[:], float64[:])], "(n)->(n)")
def demean(arr, result):
    total = 0
    count = 0

    for value in arr:
        if not np.isnan(value):
            total += value
            count += 1
    
    if count > 0:
        mean = total / count
    else:
        mean = np.nan

    for i, value in enumerate(arr):
        if not np.isnan(value):
            result[i] = value - mean
        else:
            result[i] = np.nan