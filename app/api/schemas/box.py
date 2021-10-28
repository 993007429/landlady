from app.domain.entities.box import BoxEntity
from app.domain.entities.rwmodel import RWModel


class BoxResponse(RWModel):
    box: BoxEntity


class BoxStatusResponse(RWModel):
    status: str = ''
    box: BoxEntity = None
