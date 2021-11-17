import logging
from collections import namedtuple
from typing import List, Tuple, Type, Union, Dict, Optional, Generic

from sqlalchemy import desc, Column
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, Field

from app.db.types import M

logger = logging.getLogger(__name__)

PageParams = namedtuple('PageParams', ['offset', 'limit'])


class RepoQuery(object):
    def __init__(
            self,
            params: Dict[str, Union[int, str]] = None,
            order_by: List[Tuple[Union[Column, Field], Optional[Type[desc]]]] = None,
            fields: List[Column] = None,
            page_params: PageParams = None):
        self.params = params or {}
        self.order_by = order_by or []
        self.fields = fields or []
        self.page_params = page_params or PageParams(offset=0, limit=1)


class Repository(Generic[M]):

    def __init__(self, session: Session, model_class: Type[M]):
        self.session = session
        self.model_class = model_class

    def get(self, uid: int) -> Optional[M]:
        def get_func():
            return self.session.get(entity=self.model_class, ident=uid)

        return get_func()

    def gets(self, uids: List[int]) -> List[Optional[M]]:
        return [self.get(uid) for uid in uids]

    def save(self, model: M):
        try:
            self.session.add(model)
            self.session.commit()
        except SQLAlchemyError as e:
            logger.exception(e)
            self.session.rollback()

    def update(self, id, **kwargs):
        try:
            self.session.query(self.model_class).filter_by(id=id).update(kwargs)
            self.session.commit()
        except SQLAlchemyError as e:
            logger.exception(e)
            self.session.rollback()

    def delete(self, model: M):
        try:
            self.session.query(model.__class__).filter_by(id=model.id).delete()
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            logger.exception(e)
            self.session.rollback()
        return False

    def get_models_by_query(self, repo_query: RepoQuery) -> List[Optional[M]]:
        """
        查询对象列表
        :param repo_query: a RepoQuery object which define the query detail
        :return:
        """
        if repo_query.fields:
            query = self.session.query(*repo_query.fields)
        else:
            query = self.session.query(self.model_class)
        query = query.filter_by(**repo_query.params)
        order_bys = []
        for field, _desc in repo_query.order_by:
            order_bys.append(_desc(field) if _desc else field)
        if order_bys:
            query = query.order_by(*order_bys)
        if repo_query.page_params:
            query = query.offset(repo_query.page_params.offset).limit(repo_query.page_params.limit)
        return query.all()

    def exist(self, **kwargs) -> bool:
        """
        查询是否存在
        :return:
        """
        models = self.session.query(self.model_class).filter_by(**kwargs).all()
        return len(models) > 0


class RepoGenerator(object):

    def __init__(self, session: Session):
        self._session = session

    def __call__(self, model_class: Type[M]) -> Repository[M]:
        return Repository(
            session=self._session,
            model_class=model_class
        )
