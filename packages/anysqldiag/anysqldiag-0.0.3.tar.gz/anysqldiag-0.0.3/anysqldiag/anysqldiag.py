import json
from pathlib import Path
import sys
import typing as t

import sqlglot


def anysqldiag(
    sql: str = None,
    file: str = None,
    from_stdin: bool = False,
    dialect: t.Optional[str] = None,
    error_level: t.Optional[str] = None,
    error_message_context: int = 100,
    max_errors: int = 3,
    json_indent: int = 2,
):

    if from_stdin:
        assert not sql, sql
        assert not file, file
        sql = "\n".join(sys.stdin)
    elif file:
        assert not sql, sql
        assert not from_stdin, from_stdin
        sql = Path(file).read_text()
    else:
        assert not file, file
        assert not from_stdin, from_stdin
        assert sql, sql

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
    return json_str
