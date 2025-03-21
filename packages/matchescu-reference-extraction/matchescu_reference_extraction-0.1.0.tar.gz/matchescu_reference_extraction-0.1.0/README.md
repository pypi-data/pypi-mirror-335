from matchescu.data_sources import CsvDataSource

# matchescu-reference-extraction

This package implements an entity reference extraction subsystem for entity
resolution.
The main concepts that are relevant here are:

* a generic attribute-based data record implementation (can access data by `str`
or `int` key),
* various `data_sources` which support reading records from different data
stores, and
* generic `extraction_engines` that convert data records to entity references.

# Development

Run the following commands to ensure you have a proper environment.

```shell
$ pyenv install 3.12
$ poetry install
$ poetry run pytest
```

When you contribute code, open a new `feature/*` or `hotfix/*` branch.

# Usage

```python
from matchescu.data_sources import CsvDataSource
from matchescu.extraction import Traits

traits = list(
    Traits().int(["id"])
    .string(["name", "description", "manufacturer"])
    .currency(["price"])
)
csv = CsvDataSource("./path/to/csv/file", list(traits))

```