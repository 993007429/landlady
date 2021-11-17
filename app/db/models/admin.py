from typing import Optional

from sqlmodel import Field, SQLModel

from app.db.models.common import DateTimeModelMixin


class Admin(SQLModel, DateTimeModelMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(sa_column_kwargs={'unique': True})
