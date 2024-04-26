"""Обработчик состояний чата при работе с файлом."""
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_message_in_websockets
from gateway.chat.processing_message.diploma import process_user_message_on_welcome_message_status, \
    process_user_message_on_ask_work_size_status, generate_user_plan, process_user_message_on_ask_accept_plan_status
from gateway.resources import strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import WorkWithFileChatStateEnum
from gateway.schemas.message import MessageSchema


class WorkWithFileChatStateHandler:
    """
    Обработчик состояния при работе с файлом.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            WorkWithFileChatStateEnum.WELCOME_MESSAGE: self._work_with_file_welcome_message,
            WorkWithFileChatStateEnum.FILE_ANALYZED: self._work_with_file_file_analyzed,
            WorkWithFileChatStateEnum.START_ASKING: self._work_with_file_start_asking,
        }

    @staticmethod
    async def _first_message_init(chat: ChatSchema, connections) -> None:
        """
        Обработчик первого подключения по websocket.
        Действие выполняется, когда только создается чат с пользователем и инициализируется
        первое подключение по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.WORK_WITH_FILE_WELCOME_MESSAGE,
            state=WorkWithFileChatStateEnum.WELCOME_MESSAGE,
        )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.WORK_WITH_FILE_FILE_ANALYZED,
            state=WorkWithFileChatStateEnum.FILE_ANALYZED,
        )

    async def handle_message(self, chat: ChatSchema, message: MessageSchema, connections) -> None:
        """
        Определяет какое состояние чата и вызывает соответствующий метод.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        method = self.state_methods.get(chat.chat_state)
        if method:
            await method(chat, message, connections)

    @staticmethod
    async def _work_with_file_file_analyzed(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `FILE_ANALYZED`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.WORK_WITH_FILE_START_ASKING,
            state=WorkWithFileChatStateEnum.START_ASKING,
        )

    @staticmethod
    async def _work_with_file_start_asking(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        pass
