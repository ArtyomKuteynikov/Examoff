from starlette.websockets import WebSocket

from gateway.chat.chat_states.diploma import DiplomaChatStateHandler
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import ChatType
from gateway.schemas.message import MessageSchema


class FSM(DiplomaChatStateHandler):
    async def fsm_handle_message(self, chat: ChatSchema, message: MessageSchema, connections):
        if chat.chat_type == ChatType.DIPLOMA_CHAT_TYPE:
            await DiplomaChatStateHandler.handle_message(self, chat, message, connections)

    async def init_first_message(self, chat: ChatSchema, connections):
        if chat.chat_type == ChatType.DIPLOMA_CHAT_TYPE:
            await DiplomaChatStateHandler._first_message_init(chat, connections)
