from typing import TypeVar

from app.db.models import Box, Project, User

M = TypeVar('M', Project, Box, User)
