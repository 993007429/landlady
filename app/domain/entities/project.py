from typing import List

from app.config import APPS_PATH
from app.domain.entities.rwmodel import RWModel


class ProjectEntity(RWModel):
    id: int
    name: str
    domain: str
    uat_name: str
    port_prefix: int
    url_paths: List[str]
    run_command: str = ''
    environment_variables: str = ''

    @property
    def uat_code_dir(self):
        return f'{APPS_PATH}/{self.name}'

    @property
    def uat_venv_dir(self):
        return f'{APPS_PATH}/venv/{self.name}'

    @property
    def uat_app_name(self):
        return self.name

    @property
    def uat_worker_group(self):
        return f'{self.name}-worker'

    @property
    def uat_endpoint(self):
        return f'www-uat.{self.domain}'

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        d['uatEndpoint'] = self.uat_endpoint
        return d
