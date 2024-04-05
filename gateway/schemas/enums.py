"""Module for enums."""
from enum import Enum


class StrEnum(str, Enum):  # noqa: WPS600
    """Base enum."""


class WebsocketMessageType(StrEnum):
    """
    Enum возможных типов сообщений по websocket.
    """
    USER_MESSAGE = "user_message"
