import json
import typing as t

import sqlglot


def anysqldiag(
    sql: str,
    error_level: t.Optional[str] = None,
    error_message_context: int = 100,
    max_errors: int = 3,
    dialect: str = None,
    json_indent: int = 2,
):
    error_level = (
        getattr(sqlglot.ErrorLevel, error_level.upper()) if error_level else None
    )
    diagnostics = []
    try:
        sqlglot.parse(
            sql,
            error_level=error_level,
            error_message_context=error_message_context,
            max_errors=max_errors,
            dialect=dialect,
        )
    except sqlglot.errors.ParseError as e:
        diagnostics = e.errors
    json_str = json.dumps(diagnostics, indent=json_indent)
    print(json_str)
    return diagnostics
