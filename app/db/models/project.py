from typing import Optional

from sqlmodel import Field, SQLModel

from app.db.models.common import DateTimeModelMixin


class Project(SQLModel, DateTimeModelMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={'unique': True})
    domain: str
    uat_name: str
    port_prefix: str
    run_command: str
    url_paths: str
    environment_variables: str
