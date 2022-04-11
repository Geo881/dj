"""
Node related APIs.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, SQLModel, select

from datajunction.models.column import Column
from datajunction.models.node import Node, NodeType
from datajunction.utils import get_session

_logger = logging.getLogger(__name__)
router = APIRouter()


class NodeMetadata(SQLModel):
    """
    A node with information about columns and if it is a metric.
    """

    id: int
    name: str
    description: str = ""

    created_at: datetime
    updated_at: datetime

    type: NodeType
    expression: Optional[str] = None

    columns: List[Column]


@router.get("/nodes/", response_model=List[NodeMetadata])
def read_nodes(*, session: Session = Depends(get_session)) -> List[NodeMetadata]:
    """
    List the available nodes.
    """
    return session.exec(select(Node)).all()
