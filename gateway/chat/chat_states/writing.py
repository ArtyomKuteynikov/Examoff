"""Обработчик состояний чата для заказа эссе."""
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_message_in_websockets
from gateway.chat.processing_message.diploma import process_user_message_on_welcome_message_status, \
    process_user_message_on_ask_work_size_status, generate_user_plan, process_user_message_on_ask_accept_plan_status
from gateway.resources import strings
from gateway.resources.chat_state_strings import writing_state_strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import WritingChatStateEnum
from gateway.schemas.message import MessageSchema


class WritingChatStateHandler:
    """
    Обработчик состояния для заказа эссе.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            WritingChatStateEnum.WELCOME_MESSAGE: self._writing_welcome_message,
            WritingChatStateEnum.ASK_THEME: self._writing_ask_theme,
            WritingChatStateEnum.ASK_WORK_SIZE: self._writing_ask_work_size,
            WritingChatStateEnum.ASK_OTHER_REQUIREMENTS: self._writing_ask_other_requirements,
            WritingChatStateEnum.ASK_INFORMATION_SOURCE: self._writing_ask_information_source,
            WritingChatStateEnum.ASK_WRITING_STYLE: self._writing_ask_writing_style,
            WritingChatStateEnum.ASK_ANY_INFORMATION: self._writing_ask_any_information,
            WritingChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE: self._writing_ask_accept_text_structure,
            WritingChatStateEnum.DIALOG_IS_OVER: self._writing_dialog_is_over,
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
            message_text=writing_state_strings.WRITING_WELCOME_MESSAGE,
            state=WritingChatStateEnum.WELCOME_MESSAGE,
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
    async def _writing_welcome_message(chat: ChatSchema, message: MessageSchema, connections) -> None:
        """
        Обработчик для состояния чата `WELCOME_MESSAGE`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        answer = process_user_message_on_welcome_message_status(message.text)
        if not answer:
            await repeat_state_message(
                connections=connections,
                chat=chat,
                message_text=writing_state_strings.WRITING_WELCOME_MESSAGE,
            )
        elif answer == "Survey":
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=writing_state_strings.WRITING_ASK_THEME,
                state=WritingChatStateEnum.ASK_THEME,
            )
        elif answer == "File":
            await repeat_state_message(
                connections=connections,
                chat=chat,
                message_text=strings.NOT_YET_MESSAGE,
            )

    @staticmethod
    async def _writing_ask_theme(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_WORK_SIZE,
            state=WritingChatStateEnum.ASK_WORK_SIZE,
        )

    @staticmethod
    async def _writing_ask_work_size(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_WORK_SIZE`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        answer = process_user_message_on_ask_work_size_status(message.text)
        if not answer:
            await repeat_state_message(
                connections=connections,
                chat=chat,
                message_text=writing_state_strings.WRITING_ASK_WORK_SIZE,
            )
        elif answer:
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=writing_state_strings.WRITING_ASK_OTHER_REQUIREMENTS,
                state=WritingChatStateEnum.ASK_OTHER_REQUIREMENTS,
            )

    @staticmethod
    async def _writing_ask_other_requirements(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_OTHER_REQUIREMENTS`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_INFORMATION_SOURCE,
            state=WritingChatStateEnum.ASK_INFORMATION_SOURCE,
        )

    @staticmethod
    async def _writing_ask_information_source(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_INFORMATION_SOURCE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_WRITING_STYLE,
            state=WritingChatStateEnum.ASK_WRITING_STYLE,
        )

    @staticmethod
    async def _writing_ask_writing_style(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_WRITING_STYLE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_ANY_INFORMATION,
            state=WritingChatStateEnum.ASK_ANY_INFORMATION,
        )

    @staticmethod
    async def _writing_ask_any_information(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ANY_INFORMATION`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        plan = await generate_user_plan(chat.id)
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_ACCEPT_TEXT_STRUCTURE,
            state=WritingChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
        )
        await create_system_message_in_db(
            chat=chat, text=plan, response_specific_state=WritingChatStateEnum.ASK_ANY_INFORMATION
        )
        await send_message_in_websockets(
            connections, chat, plan
        )

    @staticmethod
    async def _writing_ask_accept_text_structure(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_TEXT_STRUCTURE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_DIALOG_IS_OVER,
            state=WritingChatStateEnum.DIALOG_IS_OVER,
        )

    @staticmethod
    async def _writing_dialog_is_over(chat: ChatSchema, message, connections) -> None:
        # todo
        print('_writing_dialog_is_over')
