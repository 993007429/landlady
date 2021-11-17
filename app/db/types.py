from typing import TypeVar

from app.db.models import Box, Project, User
from app.db.models.admin import Admin

M = TypeVar('M', Project, Box, User, Admin)
