from starlette.websockets import WebSocket

from gateway.chat.chat_states.diploma import DiplomaChatStateHandler
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import ChatType


class FSM(DiplomaChatStateHandler):
    def fsm_handle_message(self, chat_type: str, chat_state: str):
        if chat_type == ChatType.DIPLOMA_CHAT_TYPE:
            DiplomaChatStateHandler.handle_message(self, chat_state)

    async def init_first_message(self, chat: ChatSchema, websocket: WebSocket, connections):
        if chat.chat_type == ChatType.DIPLOMA_CHAT_TYPE:
            await DiplomaChatStateHandler._first_message_init(chat, websocket, connections)
