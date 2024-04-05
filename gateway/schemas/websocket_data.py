"""
Dataclass WebsocketData.
"""
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
        На данный момент только один доступный вариант: `user_message`.

    data: Dict[str, Any]
        Содержит любые данные, которые должны быть переданы.
    """
    message_type: Literal[WebsocketMessageType.USER_MESSAGE]
    data: Dict[str, Any]
