from typing import List, Generic

from app.domain.entities.rwmodel import RWModel
from app.domain.types import E


class ModelListResponse(RWModel, Generic[E]):
    list: List[E]
    start: int
    perpage: int
    total: int


class SuccessResponse(RWModel):

    msg: str = '操作成功'
    