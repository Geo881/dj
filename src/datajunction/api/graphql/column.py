"""
Models for columns.
"""

from typing import TYPE_CHECKING

import strawberry

from datajunction.models.column import Column as _Column
from datajunction.typing import ColumnType as _ColumnType

if TYPE_CHECKING:
    from datajunction.models.node import Node

ColumnType = strawberry.enum(_ColumnType)


@strawberry.experimental.pydantic.type(model=_Column, all_fields=True)
class Column:  # type: ignore
    """
    A column.

    Columns can be physical (associated with ``Table`` objects) or abstract (associated
    with ``Node`` objects).
    """
