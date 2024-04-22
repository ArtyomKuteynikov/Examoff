"""Обработчик состояний чата для заказа реферата."""
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_message_in_websockets
from gateway.chat.processing_message.diploma import process_user_message_on_welcome_message_status, \
    process_user_message_on_ask_work_size_status, generate_user_plan, process_user_message_on_ask_accept_plan_status
from gateway.resources import strings
from gateway.resources.chat_state_strings import report_state_strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import ReportChatStateEnum
from gateway.schemas.message import MessageSchema


class ReportChatStateHandler:
    """
    Обработчик состояния для заказа реферата.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            ReportChatStateEnum.ASK_THEME: self._report_ask_theme,
            ReportChatStateEnum.ASK_WORK_SIZE: self._report_ask_work_size,
            ReportChatStateEnum.ASK_ASPECTS_ANALYSIS: self._report_ask_aspect_analysis,
            ReportChatStateEnum.ASK_ANALYSIS_TYPE: self._report_ask_analysis_type,
            ReportChatStateEnum.ASK_WRITING_STYLE: self._report_ask_writing_style,
            ReportChatStateEnum.ASK_ANY_INFORMATION: self._report_ask_any_information,
            ReportChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE: self._report_ask_accept_text_structure,
            ReportChatStateEnum.DIALOG_IS_OVER: self._report_dialog_is_over,
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
            message_text=report_state_strings.REPORT_WELCOME_MESSAGE,
            state=ReportChatStateEnum.WELCOME_MESSAGE,
        )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=report_state_strings.REPORT_ASK_THEME,
            state=ReportChatStateEnum.ASK_THEME,
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
    async def _report_ask_theme(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=report_state_strings.REPORT_ASK_WORK_SIZE,
            state=ReportChatStateEnum.ASK_WORK_SIZE,
        )

    @staticmethod
    async def _report_ask_work_size(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_WORK_SIZE`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        # todo Добавить обработчик сообщения
        # answer = process_user_message_on_ask_work_size_status(message.text)
        # if not answer:
        #     await repeat_state_message(
        #         connections=connections,
        #         chat=chat,
        #         message_text=report_state_strings.REPORT_ASK_WORK_SIZE,
        #     )
        # elif answer:
        #     await send_message_and_change_state(
        #         connections=connections,
        #         chat=chat,
        #         message_text=report_state_strings.REPORT_ASK_ASPECTS_ANALYSIS,
        #         state=ReportChatStateEnum.ASK_ASPECTS_ANALYSIS,
        #     )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=report_state_strings.REPORT_ASK_ASPECTS_ANALYSIS,
            state=ReportChatStateEnum.ASK_ASPECTS_ANALYSIS,
        )

    @staticmethod
    async def _report_ask_aspect_analysis(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ASPECTS_ANALYSIS`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=report_state_strings.REPORT_ASK_ANALYSIS_TYPE,
            state=ReportChatStateEnum.ASK_ANALYSIS_TYPE,
        )

    @staticmethod
    async def _report_ask_analysis_type(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ANALYSIS_TYPE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=report_state_strings.REPORT_ASK_WRITING_STYLE,
            state=ReportChatStateEnum.ASK_WRITING_STYLE,
        )

    @staticmethod
    async def _report_ask_writing_style(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_WRITING_STYLE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=report_state_strings.REPORT_ASK_ANY_INFORMATION,
            state=ReportChatStateEnum.ASK_ANY_INFORMATION,
        )

    @staticmethod
    async def _report_ask_any_information(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ANY_INFORMATION`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=report_state_strings.REPORT_ASK_ACCEPT_TEXT_STRUCTURE.format(
                report_text_structure='report_text_structure',
            ),
            state=ReportChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
        )

    @staticmethod
    async def _report_ask_accept_text_structure(chat: ChatSchema, message, connections) -> None:
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=report_state_strings.REPORT_DIALOG_IS_OVER,
            state=ReportChatStateEnum.DIALOG_IS_OVER,
        )

    @staticmethod
    async def _report_dialog_is_over(chat: ChatSchema, message, connections) -> None:
        # todo
        print('_report_dialog_is_over')
