"""Module for enums."""
from enum import Enum, auto


class StrEnum(str, Enum):  # noqa: WPS600
    """Base enum."""


class WebsocketMessageType(StrEnum):
    """
    Enum возможных типов сообщений по websocket.
    ============================================

    USER_MESSAGE.
        Сообщение, отправленное от пользователя.

    SYSTEM_MESSAGE.
        Сообщение, отправленное от backend.

    USER_MESSAGE_FROM_OTHER_SOCKET.
        Сообщение, отправленное от пользователя.
        Дублирует информацию для других websocket соединений.
    """
    USER_MESSAGE = "user_message"
    SYSTEM_MESSAGE = "system_message"
    USER_MESSAGE_FROM_OTHER_SOCKET = "user_message_from_other_socket"


class ChatType(StrEnum):
    DIPLOMA_CHAT_TYPE = "DIPLOMA_CHAT_TYPE"
