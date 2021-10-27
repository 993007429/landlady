import enum
from datetime import datetime
from typing import Optional

from app.config import BOX_ROOT, LOGS_PATH
from app.domain.entities.project import ProjectEntity
from app.domain.entities.rwmodel import RWModel
from app.domain.entities.user import UserEntity


class BoxStatus(enum.Enum):
    off = 'off'
    on = 'on'
    error = 'error'


class BoxEntity(RWModel):
    id: int
    project: Optional[ProjectEntity] = None
    user: Optional[UserEntity] = None
    status: BoxStatus = BoxStatus.off
    port_prefix: int = None
    numprocs: int = None
    start_time: Optional[datetime] = None

    @property
    def box_dir(self) -> str:
        return f'{BOX_ROOT}/{self.project.name}/box-{self.id}'

    @property
    def code_dir(self) -> str:
        return f'{self.box_dir}/{self.project.name}'

    @property
    def fe_dir(self) -> str:
        return f'{self.code_dir}/frontend_dist'

    @property
    def logs_dir(self) -> str:
        return f'{LOGS_PATH}/{self.app_name}'

    @property
    def supervisor_conf(self) -> str:
        return f'{self.box_dir}/supervisor.conf'

    @property
    def nginx_conf(self) -> str:
        return f'{self.box_dir}/nginx.conf'

    @property
    def app_name(self) -> str:
        return f'{self.project.name}-{self.id}'

    @property
    def server_name(self):
        return f'{self.uat_name}-{self.id}.{self.domain}'

    def log_file(self, process_num: int) -> str:
        return f'{self.logs_dir}/web-{self.port_prefix}{process_num}.log'
