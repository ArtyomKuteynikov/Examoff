"""Обработчик состояний чата для заказа домашнего задания."""
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_message_in_websockets
from gateway.chat.processing_message.diploma import process_user_message_on_welcome_message_status, \
    process_user_message_on_ask_work_size_status, generate_user_plan, process_user_message_on_ask_accept_plan_status
from gateway.resources import strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import HomeworkChatStateEnum
from gateway.schemas.message import MessageSchema


class HomeworkChatStateHandler:
    """
    Обработчик состояния для заказа диплома.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            HomeworkChatStateEnum.WELCOME_MESSAGE: self._homework_welcome_message,
            HomeworkChatStateEnum.ASK_THEME: self._homework_ask_theme,
            HomeworkChatStateEnum.ASK_WORK_SIZE: self._homework_ask_work_size,
            HomeworkChatStateEnum.ASK_OTHER_REQUIREMENTS: self._homework_ask_other_requirements,
            HomeworkChatStateEnum.ASK_INFORMATION_SOURCE: self._homework_ask_information_source,
            HomeworkChatStateEnum.ASK_ANY_INFORMATION: self._homework_ask_any_information,
            HomeworkChatStateEnum.ASK_ACCEPT_PLAN: self._homework_ask_accept_plan,
            HomeworkChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE: self._homework_ask_accept_text_structure,
            HomeworkChatStateEnum.DIALOG_IS_OVER: self._homework_dialog_is_over,
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
            message_text=strings.HOMEWORK_WELCOME_MESSAGE,
            state=HomeworkChatStateEnum.WELCOME_MESSAGE,
        )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.HOMEWORK_ASK_THEME,
            state=HomeworkChatStateEnum.ASK_THEME,
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
    async def _homework_ask_theme(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.HOMEWORK_ASK_WORK_SIZE,
            state=HomeworkChatStateEnum.ASK_WORK_SIZE,
        )

    @staticmethod
    async def _homework_ask_work_size(chat: ChatSchema, message, connections) -> None:
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
                message_text=strings.HOMEWORK_ASK_WORK_SIZE,
            )
        elif answer:
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=strings.HOMEWORK_ASK_OTHER_REQUIREMENTS,
                state=HomeworkChatStateEnum.ASK_OTHER_REQUIREMENTS,
            )

    @staticmethod
    async def _homework_ask_other_requirements(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_OTHER_REQUIREMENTS`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.HOMEWORK_ASK_INFORMATION_SOURCE,
            state=HomeworkChatStateEnum.ASK_INFORMATION_SOURCE,
        )

    @staticmethod
    async def _homework_ask_information_source(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_INFORMATION_SOURCE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.HOMEWORK_ASK_ANY_INFORMATION,
            state=HomeworkChatStateEnum.ASK_ANY_INFORMATION,
        )

    @staticmethod
    async def _homework_ask_any_information(chat: ChatSchema, message, connections) -> None:
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
            message_text=strings.HOMEWORK_ASK_ACCEPT_PLAN,
            state=HomeworkChatStateEnum.ASK_ACCEPT_PLAN,
        )
        await create_system_message_in_db(
            chat=chat, text=plan, response_specific_state=HomeworkChatStateEnum.ASK_ANY_INFORMATION
        )
        await send_message_in_websockets(
            connections, chat, plan
        )

    async def _homework_ask_accept_plan(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_PLAN`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        answer = process_user_message_on_ask_accept_plan_status(message.text)
        if not answer:
            await self._homework_ask_any_information(chat, message, connections)
        elif answer:
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text="todo",
                state=HomeworkChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
            )

    @staticmethod
    async def _homework_ask_accept_text_structure(chat: ChatSchema, message, connections) -> None:
        # todo
        print('_homework_ask_accept_text_structure')

    @staticmethod
    async def _homework_dialog_is_over(chat: ChatSchema, message, connections) -> None:
        print('_homework_dialog_is_over')
