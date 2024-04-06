"""
Dataclass Chat.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ChatSchema(BaseModel):
    """
    Чат, хранимый в БД.
    ===================

    Class properties
    ----------------

    id: int
        Уникальный идентификатор чата.

    chat_states: Optional[str]
        Состояния чата, которое используется для выбора взаимодействия с пользователем.

    chat_types: str
        Тип чата, определяющий его назначение.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_states: Optional[str] = None
    chat_types: str


class ChatInCreationSchema(BaseModel):
    """
    Чат перед сохранением в БД.
    ===========================

    Class properties
    ----------------

    id: int
        Уникальный идентификатор чата.

    chat_states: Optional[str]
        Состояния чата, которое используется для выбора взаимодействия с пользователем.

    chat_types: str
        Тип чата, определяющий его назначение.
    """
    id: Optional[str] = None
    chat_states: Optional[str] = None
    chat_types: str = Field(default="DIPLOMA_CHAT_TYPE")
