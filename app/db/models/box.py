from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Enum
from sqlmodel import Field, SQLModel

from app.db.models.common import DateTimeModelMixin
from app.domain.entities.box import BoxStatus


class Box(SQLModel, DateTimeModelMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int
    user_id: int
    port_prefix: Optional[int]
    numprocs: int = 1
    status: BoxStatus = Field(sa_column=Column(Enum(BoxStatus)))
    start_time: datetime = None
