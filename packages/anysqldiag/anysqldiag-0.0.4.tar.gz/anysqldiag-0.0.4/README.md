# AnySqlDiag

[![PyPI version](https://badge.fury.io/py/anysqldiag.svg)](https://badge.fury.io/py/anysqldiag)

CLI to diagnose any SQL dialects supported by [sqlglot](https://github.com/tobymao/sqlglot) package:

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

# specify dialect
anysqldiag --dialect spark "SELECT foo FROM (SELECT baz FROM t" 
```

Output:

```json
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

## Args

```
NAME
    anysqldiag

SYNOPSIS
    anysqldiag <flags>

FLAGS
    -s, --sql=SQL
        Type: Optional[str]
        Default: None
    --file=FILE
        Type: Optional[str]
        Default: None
    --from_stdin=FROM_STDIN
        Type: bool
        Default: False
    -d, --dialect=DIALECT
        Type: Optional[Optional]
        Default: None
    --error_level=ERROR_LEVEL
        Type: Optional[Optional]
        Default: None
    --error_message_context=ERROR_MESSAGE_CONTEXT
        Type: int
        Default: 100
    -m, --max_errors=MAX_ERRORS
        Type: int
        Default: 3
    -j, --json_indent=JSON_INDENT
        Type: int
        Default: 2
```

Regarding the following args, see [sqlglot.parser.Parser](https://sqlglot.com/sqlglot/parser.html#Parser).

- error_level
- error_message_context
- max_errors
