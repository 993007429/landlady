import datetime

from pydantic import BaseModel, validator
from sqlalchemy import Column, TIMESTAMP
from sqlmodel import Field


class DateTimeModelMixin(BaseModel):
    created_at: datetime.datetime = datetime.datetime.now()
    updated_at: datetime.datetime = Field(sa_column=Column(
        TIMESTAMP, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False))

    @validator("created_at", "updated_at", pre=True)
    def default_datetime(
            cls,  # noqa: N805
            value: datetime.datetime,  # noqa: WPS110
    ) -> datetime.datetime:
        return value or datetime.datetime.now()
