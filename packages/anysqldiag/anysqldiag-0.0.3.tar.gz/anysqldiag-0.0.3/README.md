# AnySqlDiag

[![PyPI version](https://badge.fury.io/py/anysqldiag.svg)](https://badge.fury.io/py/anysqldiag)

CLI to diagnose any SQL supported by [sqlglot](https://github.com/tobymao/sqlglot) package:

- Athena
- BigQuery
- ClickHouse
- Databricks
- Doris
- Drill
- Druid
- DuckDB
- Dune
- Hive
- Materialize
- MySQL
- Oracle
- Postgres
- Presto
- PRQL
- Redshift
- RisingWave
- Snowflake
- Spark
- Spark2
- SQLite
- StarRocks
- Tableau
- Teradata
- Trino
- TSQL

## Example

```bash
# auto-detect dialect
anysqldiag "SELECT foo FROM (SELECT baz FROM t"

# specify dialect in lower case
anysqldiag --dialect spark "SELECT foo FROM (SELECT baz FROM t"
```

Output:

```
[
  {
    "description": "Expecting )",
    "line": 1,
    "col": 34,
    "start_context": "SELECT foo FROM (SELECT baz FROM ",
    "highlight": "t",
    "end_context": "",
    "into_expression": null
  }
]
```
