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

    sender: str
        Тип сообщения. Определяет, как должны быть обработаны данные.

    data: Dict[str, Any]
        Содержит любые данные, которые должны быть переданы.

    Example websocket message:
        {
            "sender": "viewer",
            "data": {
                "message_text": "Hello, my name is User."
            }
        }
    """
    sender: Literal[
        WebsocketMessageType.VIEWER,
        WebsocketMessageType.SERVER,
        WebsocketMessageType.USER_MESSAGE_FROM_OTHER_SOCKET,
    ]
    data: Dict[str, Any]


def websocket_message_data_to_websocket_format(message: WebsocketMessageData) -> str:
    """
    Приводит WebsocketMessageData в словарь.

    :param message: Сообщение по websocket.
    :return: Str по примеру:
        {
            "sender": "viewer",
            "data": {
                "message_text": "Hello, my name is User."
            }
        }
    """
    return dumps({"sender": message.sender.value, "data": message.data, }, ensure_ascii=False)
