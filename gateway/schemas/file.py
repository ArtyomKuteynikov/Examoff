from typing import Optional
from pydantic import BaseModel, Field
import uuid


class FileSchema(BaseModel):
    """
    Файл, хранимый в БД.
    ====================

    Class properties
    ----------------

    id: uuid.UUID
        Уникальный идентификатор файла, который также является его названием.

    user_id: int
        Идентификатор пользователя, который может скачать файл.
    """

    id: uuid.UUID
    user_id: int


class FileCreateSchema(BaseModel):
    """
    Файл перед сохранением в БД.
    ===========================

    Class properties
    ----------------

    id: uuid.UUID
        Уникальный идентификатор файла, который также является его названием.

    user_id: int
        Идентификатор пользователя, который будет ассоциирован с файлом.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: int
