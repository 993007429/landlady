from typing import Optional

from sqlmodel import Field, SQLModel

from app.db.models.common import DateTimeModelMixin


class User(SQLModel, DateTimeModelMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={'unique': True})