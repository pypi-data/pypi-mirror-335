# vlgi-datasets

## Overview

Repositiory with custom kedro datasets

## How to use

In code:
```python
from kedro.io import DataCatalog
from vlgi_datasets import PostgresTableUpsertDataSet

io = DataCatalog(
    {
        "asset": PostgresTableUpsertDataSet(
            table_name="assets",
            credentials={"con": "myconnectionstring"},
            save_args={"if_exists": "append", "constraint": "assets_pkey"},
            overwrite_columns=False, 
        ),
    }
)
```

In catalog.yml:
```yaml
asset:
  type: vlgi_datasets.PostgresTableUpsertDataSet
  table_name: assets
  credentials:
    con: myconnectionstring
  save_args:
    if_exists: append
    constraint: assets_pkey
    overwrite_columns: False
```

#### Observation
- The `overwrite_columns` parameter is optional and defaults to `True`.
