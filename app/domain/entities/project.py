from typing import List

from app.domain.entities.rwmodel import RWModel


class ProjectEntity(RWModel):
    id: int
    name: str
    domain: str
    uat_name: str
    port_prefix: str
    url_paths: List[str]
    run_command: str = ''
    environment_variables: str = ''
