## Features

### Demean

The `demean` function subtracts the mean from each non-NaN value in an array, preserving NaN values.

```python
import polars as pl
from ethanpolars import demean

# Sample data...
df = pl.DataFrame({
    "value": [1.0, 2.0, 3.0, None, 5.0]
})

# Apply demean to the column...

print(df)
```
Output...
```