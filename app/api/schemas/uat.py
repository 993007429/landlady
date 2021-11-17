from app.domain.entities.box import BoxEntity
from app.domain.entities.rwmodel import RWModel


class UATStatusResponse(RWModel):
    status: str = ''
