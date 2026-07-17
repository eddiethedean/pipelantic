# etlantic-sqlmodel

Optional bridge between ETLantic `Data` contracts and
[SQLModel](https://sqlmodel.tiangolo.com/) table models.

```bash
pip install etlantic-sqlmodel
# or: pip install 'etlantic[sqlmodel]'
```

Sessions, Alembic migrations, and repository helpers are deferred to 1.1+.
This package focuses on schema mapping and metadata comparison only.

## Usage

```python
from etlantic import Data
from etlantic_sqlmodel import (
    compare_metadata,
    contract_to_sqlmodel,
    create_plugin,
    sqlmodel_to_contract,
)


class Customer(Data):
    customer_id: int
    name: str


CustomerTable = contract_to_sqlmodel(
    Customer,
    table_name="customer",
    primary_key=("customer_id",),
)

metadata = sqlmodel_to_contract(CustomerTable)
report = compare_metadata(Customer, CustomerTable)
assert report.valid

plugin = create_plugin()
```

Generated SQLModel classes are reviewable starting points — relational choices
such as primary keys and table names must be supplied explicitly.
