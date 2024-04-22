"""Обработчик состояний чата для заказа контрольной работы."""
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_message_in_websockets
from gateway.chat.processing_message.diploma import process_user_message_on_welcome_message_status, \
    process_user_message_on_ask_work_size_status, generate_user_plan, process_user_message_on_ask_accept_plan_status
from gateway.resources import strings
from gateway.resources.chat_state_strings import course_work_state_strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import CourseWorkChatStateEnum
from gateway.schemas.message import MessageSchema


class CourseWorkChatStateHandler:
    """
    Обработчик состояния для заказа контрольной работы.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            CourseWorkChatStateEnum.ASK_THEME: self._course_work_ask_theme,
            CourseWorkChatStateEnum.ASK_WORK_SIZE: self._course_work_ask_work_size,
            CourseWorkChatStateEnum.ASK_OTHER_REQUIREMENTS: self._course_work_ask_other_requirements,
            CourseWorkChatStateEnum.ASK_INFORMATION_SOURCE: self._course_work_ask_information_source,
            CourseWorkChatStateEnum.ASK_ANY_INFORMATION: self._course_work_ask_any_information,
            CourseWorkChatStateEnum.ASK_ACCEPT_PLAN: self._course_work_ask_accept_plan,
            CourseWorkChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE: self._course_work_ask_accept_text_structure,
            CourseWorkChatStateEnum.DIALOG_IS_OVER: self._course_work_dialog_is_over,
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
            message_text=course_work_state_strings.COURSE_WORK_WELCOME_MESSAGE,
            state=CourseWorkChatStateEnum.WELCOME_MESSAGE,
        )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_THEME,
            state=CourseWorkChatStateEnum.ASK_THEME,
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
    async def _course_work_ask_theme(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_WORK_SIZE,
            state=CourseWorkChatStateEnum.ASK_WORK_SIZE,
        )

    @staticmethod
    async def _course_work_ask_work_size(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_WORK_SIZE`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        # answer = process_user_message_on_ask_work_size_status(message.text)
        # if not answer:
        #     await repeat_state_message(
        #         connections=connections,
        #         chat=chat,
        #         message_text=course_work_state_strings.COURSE_WORK_ASK_WORK_SIZE,
        #     )
        # elif answer:
        #     await send_message_and_change_state(
        #         connections=connections,
        #         chat=chat,
        #         message_text=course_work_state_strings.COURSE_WORK_ASK_OTHER_REQUIREMENTS,
        #         state=CourseWorkChatStateEnum.ASK_OTHER_REQUIREMENTS,
        #     )
        # todo Добавить обработчик сообщения

        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_OTHER_REQUIREMENTS,
            state=CourseWorkChatStateEnum.ASK_OTHER_REQUIREMENTS,
        )

    @staticmethod
    async def _course_work_ask_other_requirements(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_OTHER_REQUIREMENTS`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_INFORMATION_SOURCE,
            state=CourseWorkChatStateEnum.ASK_INFORMATION_SOURCE,
        )

    @staticmethod
    async def _course_work_ask_information_source(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_INFORMATION_SOURCE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_ANY_INFORMATION,
            state=CourseWorkChatStateEnum.ASK_ANY_INFORMATION,
        )

    @staticmethod
    async def _course_work_ask_any_information(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ANY_INFORMATION`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        course_work_plan = await generate_user_plan(chat.id)
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_ACCEPT_PLAN.format(
                course_work_plan=course_work_plan,
            ),
            state=CourseWorkChatStateEnum.ASK_ACCEPT_PLAN,
        )

    async def _course_work_ask_accept_plan(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_PLAN`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        # todo Добавить обработчик сообщения
        # answer = process_user_message_on_ask_accept_plan_status(message.text)
        # if not answer:
        #     await self._course_work_ask_any_information(chat, message, connections)
        # elif answer:
        #     await send_message_and_change_state(
        #         connections=connections,
        #         chat=chat,
        #         message_text="todo",
        #         state=CourseWorkChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
        #     )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_ACCEPT_TEXT_STRUCTURE.format(
                course_work_text_structure='course_work_text_structure',
            ),
            state=CourseWorkChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
        )

    @staticmethod
    async def _course_work_ask_accept_text_structure(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_TEXT_STRUCTURE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_DIALOG_IS_OVER,
            state=CourseWorkChatStateEnum.DIALOG_IS_OVER,
        )

    @staticmethod
    async def _course_work_dialog_is_over(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `DIALOG_IS_OVER`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        # todo
