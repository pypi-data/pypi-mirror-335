from numba import float64, guvectorize
import numpy as np
import polars as pl

@guvectorize([(float64[:], float64[:])], "(n)->(n)")
def _demean(arr, result):
    """Internal implementation of demean."""
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

def demean(series: pl.Series) -> pl.Series:
    """
    Subtracts the mean from each value in a series. Null values are preserved
    and do not contrbiute to cardinality.

    Null values are converted to NaN on the fly, as generalized ufuncs do not accept
    the former."
    """
    filled = series.fill_null(np.nan)
    result = _demean(filled)
    return result.fill_nan(None)
