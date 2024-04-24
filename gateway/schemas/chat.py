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

    user_owner_id: int
        Идентификатор владельца чата.

    chat_state: Optional[str]
        Состояния чата, которое используется для выбора взаимодействия с пользователем.

    chat_type: str
        Тип чата, определяющий его назначение.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_owner_id: int
    chat_state: Optional[str] = None
    chat_type: str


class ChatInCreationSchema(BaseModel):
    """
    Чат перед сохранением в БД.
    ===========================

    Class properties
    ----------------

    id: int
        Уникальный идентификатор чата.

    user_owner_id: int
        Идентификатор владельца чата.

    chat_state: Optional[str]
        Состояния чата, которое используется для выбора взаимодействия с пользователем.

    chat_type: str
        Тип чата, определяющий его назначение.
    """
    id: Optional[int] = None
    user_owner_id: int
    chat_state: Optional[str] = None
    chat_type: str = Field(default="DIPLOMA_CHAT_TYPE")
