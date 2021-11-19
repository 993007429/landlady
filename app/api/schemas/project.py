from app.domain.entities.project import ProjectEntity
from app.domain.entities.rwmodel import RWModel


class ProjectResponse(RWModel):
    project: ProjectEntity


class UATStatusResponse(RWModel):
    status: str = ''


