"""Обработчик состояний чата для заказа диплома."""
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_message_in_websockets
from gateway.chat.processing_message.diploma import process_user_message_on_welcome_message_status, \
    process_user_message_on_ask_work_size_status, generate_user_plan, process_user_message_on_ask_accept_plan_status
from gateway.resources import strings
from gateway.resources.chat_state_strings import diploma_state_strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import DiplomaChatStateEnum
from gateway.schemas.message import MessageSchema


class DiplomaChatStateHandler:
    """
    Обработчик состояния для заказа диплома.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            DiplomaChatStateEnum.ASK_THEME: self._diploma_ask_theme,
            DiplomaChatStateEnum.ASK_WORK_SIZE: self._diploma_ask_work_size,
            DiplomaChatStateEnum.ASK_OTHER_REQUIREMENTS: self._diploma_ask_other_requirements,
            DiplomaChatStateEnum.ASK_INFORMATION_SOURCE: self._diploma_ask_information_source,
            DiplomaChatStateEnum.ASK_ANY_INFORMATION: self._diploma_ask_any_information,
            DiplomaChatStateEnum.ASK_ACCEPT_PLAN: self._diploma_ask_accept_plan,
            DiplomaChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE: self._diploma_ask_accept_text_structure,
            DiplomaChatStateEnum.DIALOG_IS_OVER: self._diploma_dialog_is_over,
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
            message_text=diploma_state_strings.DIPLOMA_WELCOME_MESSAGE,
            state=DiplomaChatStateEnum.WELCOME_MESSAGE,
        )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=diploma_state_strings.DIPLOMA_ASK_THEME,
            state=DiplomaChatStateEnum.ASK_THEME,
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
    async def _diploma_ask_theme(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=diploma_state_strings.DIPLOMA_ASK_WORK_SIZE,
            state=DiplomaChatStateEnum.ASK_WORK_SIZE,
        )

    @staticmethod
    async def _diploma_ask_work_size(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_WORK_SIZE`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        # Todo Добавить обработчик сообщения.
        # answer = process_user_message_on_ask_work_size_status(message.text)
        # if not answer:
        #     await repeat_state_message(
        #         connections=connections,
        #         chat=chat,
        #         message_text=diploma_state_strings.DIPLOMA_ASK_WORK_SIZE,
        #     )
        # elif answer:
        #     await send_message_and_change_state(
        #         connections=connections,
        #         chat=chat,
        #         message_text=diploma_state_strings.DIPLOMA_ASK_OTHER_REQUIREMENTS,
        #         state=DiplomaChatStateEnum.ASK_OTHER_REQUIREMENTS,
        #     )

        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=diploma_state_strings.DIPLOMA_ASK_OTHER_REQUIREMENTS,
            state=DiplomaChatStateEnum.ASK_OTHER_REQUIREMENTS,
        )

    @staticmethod
    async def _diploma_ask_other_requirements(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_OTHER_REQUIREMENTS`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=diploma_state_strings.DIPLOMA_ASK_INFORMATION_SOURCE,
            state=DiplomaChatStateEnum.ASK_INFORMATION_SOURCE,
        )

    @staticmethod
    async def _diploma_ask_information_source(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_INFORMATION_SOURCE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=diploma_state_strings.DIPLOMA_ASK_ANY_INFORMATION,
            state=DiplomaChatStateEnum.ASK_ANY_INFORMATION,
        )

    @staticmethod
    async def _diploma_ask_any_information(chat: ChatSchema, message, connections) -> None:
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
            message_text=diploma_state_strings.DIPLOMA_ASK_ACCEPT_PLAN.format(
                diploma_plan='diploma_plan'  # todo
            ),
            state=DiplomaChatStateEnum.ASK_ACCEPT_PLAN,
        )

    async def _diploma_ask_accept_plan(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_PLAN`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        # """
        # answer = process_user_message_on_ask_accept_plan_status(message.text)
        # if not answer:
        #     await self._diploma_ask_any_information(chat, message, connections)
        # elif answer:
        #     await send_message_and_change_state(
        #         connections=connections,
        #         chat=chat,
        #         message_text="todo",
        #         state=DiplomaChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
        #     )
        # todo Добавить обработчик сообщения

        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=diploma_state_strings.DIPLOMA_ASK_ACCEPT_TEXT_STRUCTURE.format(
                text_structure='text_structure'  # todo
            ),
            state=DiplomaChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
        )

    @staticmethod
    async def _diploma_ask_accept_text_structure(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_TEXT_STRUCTURE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=diploma_state_strings.DIPLOMA_DIALOG_IS_OVER,
            state=DiplomaChatStateEnum.DIALOG_IS_OVER,
        )

    @staticmethod
    async def _diploma_dialog_is_over(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `DIALOG_IS_OVER`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        # todo
