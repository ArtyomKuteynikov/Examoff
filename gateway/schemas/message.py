"""
Dataclass Message.
"""
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageSchema(BaseModel):
    """
    Сообщение пользователя, хранимое в БД.
    =======================================

    Class properties
    ----------------

    id: int
        Уникальный идентификатор сообщения.

    chat_id: int
        Идентификатор чата, к которому принадлежит сообщение.

    text: str
        Текст сообщения.
        Содержит собственно текст, отправленный пользователем.
        Example: "You are a helpful, pattern-following assistant that translates corporate jargon into English."

    sender_id: int
        Идентификатор пользователя, отправившего сообщение.

    created_at: datetime
        Дата и время создания сообщения.
        Example: 2023-04-01T12:00:00
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    text: str
    sender_id: int
    created_at: datetime
    response_specific_state: Optional[str] = None


class MessageInCreationSchema(BaseModel):
    """
    Сообщение пользователя, перед сохранением в БД.
    ===============================================

    Class properties
    ----------------

    id: int
        Уникальный идентификатор сообщения.

    chat_id: int
        Идентификатор чата, к которому принадлежит сообщение.

    text: str
        Текст сообщения.
        Содержит собственно текст, отправленный пользователем.
        Example: "You are a helpful, pattern-following assistant that translates corporate jargon into English."

    sender_id: int
        Идентификатор пользователя, отправившего сообщение.

    created_at: datetime
        Дата и время создания сообщения.
        Example: 2023-04-01T12:00:00

    response_specific_state: #todo
    """
    id: Optional[int] = None
    chat_id: int
    text: str
    sender_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    response_specific_state: Optional[str] = None
