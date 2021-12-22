from typing import Optional

from sqlalchemy import Column, Enum
from sqlmodel import Field, SQLModel

from app.db.models.common import DateTimeModelMixin
from app.domain.entities.project import ProjectDeployType


class Project(SQLModel, DateTimeModelMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={'unique': True})
    deploy_type: ProjectDeployType = Field(sa_column=Column(Enum(ProjectDeployType)))
    domain: str
    uat_name: str
    port_prefix: int
    run_command: str
    url_paths: str
    environment_variables: str
