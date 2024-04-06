from gateway.chat.chat_states.diploma import DiplomaChatStateHandler
from gateway.schemas.enums import ChatType


class FSM(DiplomaChatStateHandler):
    def fsm_handle_message(self, chat_type: str, chat_state: str):
        if chat_type == ChatType.DIPLOMA_CHAT_TYPE:
            DiplomaChatStateHandler.handle_message(self, chat_state)
