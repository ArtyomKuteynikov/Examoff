"""SQLAlchemy helpers."""

from typing import Callable

from sqlalchemy.ext.asyncio import (
    AsyncSession,

)
from sqlalchemy.orm import declarative_base

AsyncSessionFactory = Callable[..., AsyncSession]
Base = declarative_base()
