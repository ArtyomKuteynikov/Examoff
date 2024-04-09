"""
Dataclass WebsocketData.
"""
from json import dumps
from typing import Dict, Any, Literal

from pydantic import BaseModel

from gateway.schemas.enums import WebsocketMessageType


class WebsocketMessageData(BaseModel):
    """
    Представляет данные, отправляемые или получаемые через WebSocket соединение.
    ============================================================================

    Class properties
    ----------------

    message_type: str
        Тип сообщения. Определяет, как должны быть обработаны данные.

    data: Dict[str, Any]
        Содержит любые данные, которые должны быть переданы.

    Example websocket message:
        {
            "message_type": "user_message",
            "data": {
                "message_text": "Hello, my name is User."
            }
        }
    """
    message_type: Literal[
        WebsocketMessageType.USER_MESSAGE,
        WebsocketMessageType.SYSTEM_MESSAGE,
        WebsocketMessageType.USER_MESSAGE_FROM_OTHER_SOCKET,
    ]
    data: Dict[str, Any]


def websocket_message_data_to_websocket_format(message: WebsocketMessageData) -> str:
    """
    Приводит WebsocketMessageData в словарь.

    :param message: Сообщение по websocket.
    :return: Str по примеру:
        {
            "message_type": "user_message",
            "data": {
                "message_text": "Hello, my name is User."
            }
        }
    """
    return dumps({"message_type": message.message_type.value, "data": message.data, }, ensure_ascii=False)
