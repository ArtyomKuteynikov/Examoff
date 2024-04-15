"""Обработчик состояний чата для заказа эссе."""
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_message_in_websockets
from gateway.chat.processing_message.diploma import process_user_message_on_welcome_message_status, \
    process_user_message_on_ask_work_size_status, generate_user_plan, process_user_message_on_ask_accept_plan_status
from gateway.resources import strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import EssayChatStateEnum
from gateway.schemas.message import MessageSchema


class EssayChatStateHandler:
    """
    Обработчик состояния для заказа эссе.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            EssayChatStateEnum.WELCOME_MESSAGE: self._essay_welcome_message,
            EssayChatStateEnum.ASK_THEME: self._essay_ask_theme,
            EssayChatStateEnum.ASK_WORK_SIZE: self._essay_ask_work_size,
            EssayChatStateEnum.ASK_OTHER_REQUIREMENTS: self._essay_ask_other_requirements,
            EssayChatStateEnum.ASK_INFORMATION_SOURCE: self._essay_ask_information_source,
            EssayChatStateEnum.ASK_ASPECTS_PROBLEM: self._essay_ask_aspects_problem,
            EssayChatStateEnum.ASK_OPINION: self._essay_ask_opinion,
            EssayChatStateEnum.ASK_WRITING_STYLE: self._essay_ask_writing_style,
            EssayChatStateEnum.ASK_ANY_INFORMATION: self._essay_ask_any_information,
            EssayChatStateEnum.ASK_ACCEPT_PLAN: self._essay_ask_accept_plan,
            EssayChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE: self._essay_ask_accept_text_structure,
            EssayChatStateEnum.DIALOG_IS_OVER: self._essay_dialog_is_over,
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
            message_text=strings.ESSAY_WELCOME_MESSAGE,
            state=EssayChatStateEnum.WELCOME_MESSAGE,
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
    async def _essay_welcome_message(chat: ChatSchema, message: MessageSchema, connections) -> None:
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
                message_text=strings.ESSAY_WELCOME_MESSAGE,
            )
        elif answer == "Survey":
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=strings.ESSAY_ASK_THEME,
                state=EssayChatStateEnum.ASK_THEME,
            )
        elif answer == "File":
            await repeat_state_message(
                connections=connections,
                chat=chat,
                message_text=strings.NOT_YET_MESSAGE,
            )

    @staticmethod
    async def _essay_ask_theme(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.ESSAY_ASK_WORK_SIZE,
            state=EssayChatStateEnum.ASK_WORK_SIZE,
        )

    @staticmethod
    async def _essay_ask_work_size(chat: ChatSchema, message, connections) -> None:
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
                message_text=strings.ESSAY_ASK_WORK_SIZE,
            )
        elif answer:
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=strings.ESSAY_ASK_OTHER_REQUIREMENTS,
                state=EssayChatStateEnum.ASK_OTHER_REQUIREMENTS,
            )

    @staticmethod
    async def _essay_ask_other_requirements(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_OTHER_REQUIREMENTS`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.ESSAY_ASK_INFORMATION_SOURCE,
            state=EssayChatStateEnum.ASK_INFORMATION_SOURCE,
        )

    @staticmethod
    async def _essay_ask_information_source(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_INFORMATION_SOURCE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.ESSAY_ASK_ASPECTS_PROBLEM,
            state=EssayChatStateEnum.ASK_ASPECTS_PROBLEM,
        )

    @staticmethod
    async def _essay_ask_aspects_problem(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ASPECTS_PROBLEM`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.ESSAY_ASK_OPINION,
            state=EssayChatStateEnum.ASK_OPINION,
        )

    @staticmethod
    async def _essay_ask_opinion(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_OPINION`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.ESSAY_ASK_WRITING_STYLE,
            state=EssayChatStateEnum.ASK_WRITING_STYLE,
        )

    @staticmethod
    async def _essay_ask_writing_style(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_WRITING_STYLE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.ESSAY_ASK_ANY_INFORMATION,
            state=EssayChatStateEnum.ASK_ANY_INFORMATION,
        )

    @staticmethod
    async def _essay_ask_any_information(chat: ChatSchema, message, connections) -> None:
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
            message_text=strings.ESSAY_ASK_ACCEPT_PLAN,
            state=EssayChatStateEnum.ASK_ACCEPT_PLAN,
        )
        await create_system_message_in_db(
            chat=chat, text=plan, response_specific_state=EssayChatStateEnum.ASK_ANY_INFORMATION
        )
        await send_message_in_websockets(
            connections, chat, plan
        )

    async def _essay_ask_accept_plan(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_PLAN`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        answer = process_user_message_on_ask_accept_plan_status(message.text)
        if not answer:
            await self._essay_ask_any_information(chat, message, connections)
        elif answer:
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text="todo",
                state=EssayChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
            )

    @staticmethod
    async def _essay_ask_accept_text_structure(chat: ChatSchema, message, connections) -> None:
        # todo
        print('_essay_ask_accept_text_structure')

    @staticmethod
    async def _essay_dialog_is_over(chat: ChatSchema, message, connections) -> None:
        # todo
        print('_essay_dialog_is_over')
