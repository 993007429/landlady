from functools import cached_property
from typing import TypeVar

from app.domain.adapters import EntityAdapter
from app.infra.repository import RepoGenerator


class BaseService(object):
    def __init__(self, repo_generator: RepoGenerator):
        self._repo_generator = repo_generator

    @cached_property
    def entity_adapter(self) -> EntityAdapter:
        return EntityAdapter(self._repo_generator)
