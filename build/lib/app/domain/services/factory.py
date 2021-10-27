from typing import Callable, Type

from fastapi import Depends

from app.db.session import Session, get_session
from app.domain.types import S
from app.infra.repository import RepoGenerator


class ServiceFactory(object):

    _shared_instances = {}

    @classmethod
    def shared_service(cls, service_class: Type[S]) -> S:
        return cls._shared_instances.setdefault(
            service_class.__name__, cls.new_service(get_session(), service_class=service_class))

    @classmethod
    def new_service(cls, session: Session, service_class: Type[S]) -> S:
        return service_class(
            repo_generator=RepoGenerator(session=session)
        )

    @classmethod
    def dependency(cls, service_class: Type[S]) -> Callable[[Session], S]:
        def _get_service(
                session: Session = Depends(get_session),
        ) -> S:
            return cls.new_service(session=session, service_class=service_class)

        return _get_service
