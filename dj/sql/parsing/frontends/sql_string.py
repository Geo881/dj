"""
Transform a DJ AST into a sql string
"""

from functools import singledispatch
from typing import Any

from dj.sql.parsing.ast import (
    Alias,
    BinaryOp,
    Case,
    Column,
    From,
    Function,
    Join,
    Node,
    Query,
    Select,
    String,
    Table,
    UnaryOp,
    Value,
    Wildcard,
)


@singledispatch
def sql(node: Any) -> str:
    """
    return the ansi sql representing the sub-ast
    """
    raise Exception("Can only convert Node types to sql")


@sql.register
def _(node: Node) -> str:
    return " ".join([sql(child) for child in node.children])


@sql.register
def _(node: UnaryOp) -> str:
    return f"{node.op} {sql(node.expr)}"


@sql.register
def _(node: BinaryOp) -> str:
    return f"{sql(node.left)} {node.op.value} {sql(node.right)}"


@sql.register
def _(node: Function) -> str:
    return f"{node.quoted_name}({', '.join(sql(arg) for arg in node.args)})"


@sql.register
def _(node: Case) -> str:
    branches = "\n\tWHEN ".join(
        f"{sql(cond)} THEN {sql(result)}"
        for cond, result in zip(node.conditions, node.results)
    )
    return f"""(CASE
    WHEN {branches}
    ELSE {sql(node.else_result)}
END)"""


@sql.register
def _(node: Value) -> str:
    if isinstance(node, String):
        return f"'{node.value}'"
    return str(node.value)


@sql.register
def _(node: Alias) -> str:
    return f"{sql(node.child)} AS {node.quoted_name}"


@sql.register
def _(node: Column) -> str:
    if node.table:
        return f'{node.quote_style if node.quote_style else ""}{node.table.alias_or_name()}.{node.name}{node.quote_style if node.quote_style else ""}'  # pylint: disable=C0301
    return node.quoted_name


@sql.register
def _(node: Wildcard) -> str:  # pylint: disable=W0613
    return "*"


@sql.register
def _(node: Table) -> str:
    return node.quoted_name


@sql.register
def _(node: Join) -> str:
    return f"""{node.kind.value} {sql(node.table)}
        ON {sql(node.on)}"""


@sql.register
def _(node: From) -> str:
    return (
        f"FROM {sql(node.table)}" + "\n" + "\n".join(sql(join) for join in node.joins)
    )


@sql.register
def _(node: Select) -> str:
    projection = ",\n\t".join(sql(exp) for exp in node.projection)
    return f"""SELECT {"DISTINCT " if node.distinct else ""}{projection}
{sql(node.from_)}
{"WHERE "+sql(node.where) if node.where is not None else ""}
{"GROUP BY "+", ".join(sql(exp) for exp in node.group_by) if node.group_by else ""}
{"HAVING "+sql(node.having) if node.having is not None else ""}
{"LIMIT "+sql(node.limit) if node.limit is not None else ""}
""".strip()


@sql.register
def _(node: Query) -> str:

    ctes = ",\n".join(f"{cte.name} AS ({sql(cte.child)})" for cte in node.ctes)
    return (
        f"""{'WITH' if ctes else ""}
{ctes}

{("(" if node.subquery else "")+sql(node.select)+(")" if node.subquery else "")}
    """.strip()
        + "\n"
    )
