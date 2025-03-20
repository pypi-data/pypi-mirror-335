from typing import TYPE_CHECKING

import pyarrow as pa

from spiral.expressions.base import Expr, ExprLike

if TYPE_CHECKING:
    from spiral import Table


def ref(expr: ExprLike, field: str | None = None) -> Expr:
    """Store binary values as references. This expression can only be used on write.

    It is often better to store large cell values, such as bytes columns, that aren't used in filter expressions as
    references. This enables more efficient scan pruning. Many of the Spiral's cell pushdown expressions work
    over references.

    Args:
        expr: The expression to store as a reference.
        field: If the expr evaluates into struct, the field name of that struct that should be referenced.
            If `None`, the expr must evaluate into a type that supports referencing.
    """
    from spiral import _lib
    from spiral.expressions import lift

    expr = lift(expr)
    return Expr(_lib.spql.expr.ref(expr.__expr__, field))


def deref(expr: ExprLike | str, field: str | None = None, *, table: "Table" = None) -> Expr:
    """De-reference referenced values.

    See `ref` for more information on Spiral's reference values. This expression is used to de-reference referenced
    column back into their original form, e.g. binary.

    Args:
        expr: The expression to de-reference. A str is assumed to be the `se.keyed` expression.
        field: If the expr evaluates into struct, the field name of that struct that should be de-referenced.
            If `None`, the expr must evaluate into a reference type.
        table (optional): The table to de-reference from, if not available in input expression.
    """
    from spiral import _lib
    from spiral.expressions import keyed, lift

    if isinstance(expr, str):
        expr = keyed(
            expr,
            pa.struct([("__ref__", pa.struct([("id", pa.string()), ("begin", pa.uint64()), ("end", pa.uint64())]))]),
        )

    expr = lift(expr)
    return Expr(_lib.spql.expr.deref(expr.__expr__, field=field, table=table._table if table is not None else None))


def nbytes(expr: ExprLike) -> Expr:
    """Return the number of bytes in a reference.

    Args:
        expr: The ref expression to get the number of bytes from.
    """
    from spiral.expressions import lift

    expr = lift(expr)
    return expr["__ref__"]["end"] - expr["__ref__"]["begin"]
