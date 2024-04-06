"""Module for enums."""
from enum import Enum, auto

from starlette.websockets import WebSocket

from gateway.chat.processing_message.diploma import process_user_message_on_welcome_message_status
from gateway.config.database import get_db, add_messages_to_database
from gateway.db.chats.repo import ChatRepo
from gateway.resources import strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import WebsocketMessageType
from gateway.schemas.message import MessageInCreationSchema, MessageSchema
from gateway.schemas.websocket_data import WebsocketMessageData, websocket_message_data_to_websocket_format


class StrEnum(str, Enum):  # noqa: WPS600
    """Base enum."""


class DiplomaChatStateEnum(StrEnum):
    """
    Состояние диалога при заказе дипломной работы
    """
    # Бот спрашивает: Прикрепить файл или приступить к написанию работы
    WELCOME_MESSAGE = "welcome_message"

    # Бот спрашивает: Какая тема вашей дипломной работы
    ASK_THEME = "ask_theme"

    # Бот спрашивает: Сколько страниц у дипломной работы
    ASK_PAGE_NUMBER = "ask_page_number"

    # Бот спрашивает: Конкретные требования
    ASK_OTHER_REQUIREMENTS = "ask_other_requirements"

    # Бот спрашивает: Источники информаций (литературы)
    ASK_INFORMATION_SOURCE = "ask_information_source"

    # Бот спрашивает: Напиши дополнительную информацию в чате
    ASK_ANY_INFORMATION = "ask_any_information"

    # Бот спрашивает: Нормальный ли план
    ASK_ACCEPT_PLAN = "ask_accept_plan"

    # Бот спрашивает: Правильная ли структура текста
    ASK_ACCEPT_TEXT_STRUCTURE = "ask_accept_text_structure"

    # Бот скидывает документ. Окончание диалога
    DIALOG_IS_OVER = "dialog_is_over"


class DiplomaChatStateHandler:
    def __init__(self):
        self.state_methods = {
            DiplomaChatStateEnum.WELCOME_MESSAGE: self._diploma_welcome_message,
            DiplomaChatStateEnum.ASK_THEME: self._diploma_ask_theme,
            DiplomaChatStateEnum.ASK_PAGE_NUMBER: self._diploma_ask_page_number,
            DiplomaChatStateEnum.ASK_OTHER_REQUIREMENTS: self._diploma_ask_other_requirements,
            DiplomaChatStateEnum.ASK_INFORMATION_SOURCE: self._diploma_ask_information_source,
            DiplomaChatStateEnum.ASK_ANY_INFORMATION: self._diploma_ask_any_information,
            DiplomaChatStateEnum.ASK_ACCEPT_PLAN: self._diploma_ask_accept_plan,
            DiplomaChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE: self._diploma_ask_accept_text_structure,
            DiplomaChatStateEnum.DIALOG_IS_OVER: self._diploma_dialog_is_over,
        }

    @staticmethod
    async def _first_message_init(chat: ChatSchema, connections):
        # Отправляет сообщение по websockets.
        websocket_message = WebsocketMessageData(
            message_type=WebsocketMessageType.SYSTEM_MESSAGE,
            data={
                "message_text": strings.DIPLOMA_WELCOME_MESSAGE
            },
        )
        for connect in connections[chat.id]:
            data = websocket_message_data_to_websocket_format(websocket_message)
            await connect.send_text(data)

        # Записывает сообщение в БД.
        message_in_creation = MessageInCreationSchema(
            chat_id=chat.id,
            text=strings.DIPLOMA_WELCOME_MESSAGE,
            sender_id=1,  # todo Change to Admin ID
        )
        await add_messages_to_database(message_in_creation)

        # Обновляет состояние в базе.
        async for session in get_db():
            chat_repo = ChatRepo(session)
            chat.chat_state = DiplomaChatStateEnum.WELCOME_MESSAGE
            await chat_repo.update_chat(chat)

    async def handle_message(self, chat: ChatSchema, message: MessageSchema, connections):
        method = self.state_methods.get(chat.chat_state)
        if method:
            await method(chat, message, connections)

    @staticmethod
    async def _diploma_welcome_message(chat: ChatSchema, message: MessageSchema, connections):
        answer = process_user_message_on_welcome_message_status(message.text)
        if answer == 0:
            pass
        elif answer == 1:
            # Отправляет сообщение по websockets.
            websocket_message = WebsocketMessageData(
                message_type=WebsocketMessageType.SYSTEM_MESSAGE,
                data={
                    "message_text": strings.DIPLOMA_ASK_THEME
                },
            )
            for connect in connections[chat.id]:
                data = websocket_message_data_to_websocket_format(websocket_message)
                await connect.send_text(data)

            # Записывает сообщение в БД.
            message_in_creation = MessageInCreationSchema(
                chat_id=chat.id,
                text=strings.DIPLOMA_ASK_THEME,
                sender_id=1,  # todo Change to Admin ID
            )
            await add_messages_to_database(message_in_creation)

            # Обновляет состояние в базе.
            async for session in get_db():
                chat_repo = ChatRepo(session)
                chat.chat_state = DiplomaChatStateEnum.ASK_THEME
                await chat_repo.update_chat(chat)
            pass
        elif answer == 2:
            pass

    async def _diploma_ask_theme(self, chat: ChatSchema, message, connections):
        print('_diploma_ask_theme')

    async def _diploma_ask_page_number(self, chat: ChatSchema, message, connections):
        print('_diploma_ask_page_number')

    async def _diploma_ask_other_requirements(self, chat: ChatSchema, message, connections):
        print('_diploma_ask_other_requirements')

    async def _diploma_ask_information_source(self, chat: ChatSchema, message, connections):
        print('_diploma_ask_information_source')

    async def _diploma_ask_any_information(self, chat: ChatSchema, message, connections):
        print('_diploma_ask_any_information')

    async def _diploma_ask_accept_plan(self, chat: ChatSchema, message, connections):
        print('_diploma_ask_accept_plan')

    async def _diploma_ask_accept_text_structure(self, chat: ChatSchema, message, connections):
        print('_diploma_ask_accept_text_structure')

    async def _diploma_dialog_is_over(self, chat: ChatSchema, message, connections):
        print('_diploma_dialog_is_over')
