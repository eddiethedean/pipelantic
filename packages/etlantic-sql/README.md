# etlantic-sql

PostgreSQL reference SQL execution plugin for [ETLantic](https://github.com/eddiethedean/etlantic).

```bash
pip install etlantic-sql
# or: pip install 'etlantic[sql]'
export ETLANTIC_SQL_URL=postgresql+psycopg://user:pass@localhost:5432/etlantic
# SQLite is fine for demos only:
# export ETLANTIC_SQL_URL=sqlite+pysqlite:///:memory:
```

Uses SQLAlchemy Core. Driver dependencies stay out of `etlantic` core.

## Wiring

```python
from etlantic import Profile

Profile(name="sql-prod", sql_engine="sql")
```

Register `@Transformation.implementation("sql")` handlers that take
`RelationRef` inputs and return SQL query handles (not fetched rows).

## Capabilities (0.6)

- SQL→SQL fusion without intermediate Python row fetch
- Durable run-scoped staging tables (not session TEMP)
- Insert-select / CTAS-style publication
- Fail-closed planning when required capabilities are missing

**Not included:** `MERGE` / upsert (`sql_merge=False`). Requiring merge fails
at planning.

## Examples

```bash
python examples/sql_to_sql.py
python examples/sql_boundary_hybrid.py
python examples/sql_transactional_write.py
python examples/sql_failure_recovery.py
```
