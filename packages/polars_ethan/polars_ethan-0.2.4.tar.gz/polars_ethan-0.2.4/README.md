polars-ethan is a Python library that adds useful functions for use with [Polars](https://github.com/pola-rs/polars). This is also my first 
published package, so it is a good exercsie. 

## Features

### Demean

The `demean` function subtracts the mean from each non-NaN value in an array, preserving NaN values.

```python
import polars as pl
from ethanpolars import demean

# Sample data...
cameras = pl.DataFrame(
    {
        "brand": ["Leica", "Leica", "Leica", "Mamiya", "Mamiya", "Mamiya"],
        "model": ["MP", "M4", "M7", "RB67", "7II", "645 Pro"],
        "price": [6000, 10000, None, 600, 3000, 900],
    }
)

cameras = cameras.with_columns(
    pl.col('price')
    .fill_null(np.nan)
    .map_batches(demean)
    .over(pl.col("brand"))
    .fill_nan(None)
    .alias('d_price')
)

print(cameras)
```
Output:
```
┌────────┬─────────┬───────┬─────────┐
│ brand  ┆ model   ┆ price ┆ d_price │
│ ---    ┆ ---     ┆ ---   ┆ ---     │
│ str    ┆ str     ┆ i64   ┆ f64     │
╞════════╪═════════╪═══════╪═════════╡
│ Leica  ┆ MP      ┆ 6000  ┆ -2000.0 │
│ Leica  ┆ M4      ┆ 10000 ┆ 2000.0  │
│ Leica  ┆ M7      ┆ null  ┆ null    │
│ Mamiya ┆ RB67    ┆ 600   ┆ -900.0  │
│ Mamiya ┆ 7II     ┆ 3000  ┆ 1500.0  │
│ Mamiya ┆ 645 Pro ┆ 900   ┆ -600.0  │
└────────┴─────────┴───────┴─────────┘
```
Note how null values must be converted to NaN before being passed to the function.
Generalized ufuncs do not except null values, but NaN's are fine and behave how we like.
