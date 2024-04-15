"""FSM"""
from gateway.chat.chat_states.control_work import ControlWorkChatStateHandler
from gateway.chat.chat_states.diploma import DiplomaChatStateHandler
from gateway.chat.chat_states.essay import EssayChatStateHandler
from gateway.chat.chat_states.full_report import FullReportChatStateHandler
from gateway.chat.chat_states.homework import HomeworkChatStateHandler
from gateway.chat.chat_states.report import ReportChatStateHandler
from gateway.chat.chat_states.work_with_file import WorkWithFileChatStateHandler
from gateway.chat.chat_states.writing import WritingChatStateHandler
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import ChatType
from gateway.schemas.message import MessageSchema


class FSM(
    DiplomaChatStateHandler,
    ControlWorkChatStateHandler,
    EssayChatStateHandler,
    WritingChatStateHandler,
    ReportChatStateHandler,
    FullReportChatStateHandler,
    HomeworkChatStateHandler,
    WorkWithFileChatStateHandler,
):
    """
    Конечный автомат (Finite State Machine).
    Назначает для разных типов работ конкретные обработчики запросов.

    Пример:
        Заказ на дипломную работу. Для дипломной работы назначается обработчик `DiplomaChatStateHandler`.
    """

    async def fsm_handle_message(self, chat: ChatSchema, message: MessageSchema, connections) -> None:
        """
        Перенаправляет сообщение к нужному обработчику.
        """
        if chat.chat_type == ChatType.DIPLOMA_CHAT_TYPE:
            await DiplomaChatStateHandler.handle_message(self, chat, message, connections)
        elif chat.chat_type == ChatType.CONTROL_WORK_CHAT_TYPE:
            await ControlWorkChatStateHandler.handle_message(self, chat, message, connections)
        elif chat.chat_type == ChatType.ESSAY_CHAT_TYPE:
            await EssayChatStateHandler.handle_message(self, chat, message, connections)
        elif chat.chat_type == ChatType.WRITING_CHAT_TYPE:
            await WritingChatStateHandler.handle_message(self, chat, message, connections)
        elif chat.chat_type == ChatType.REPORT_CHAT_TYPE:
            await ReportChatStateHandler.handle_message(self, chat, message, connections)
        elif chat.chat_type == ChatType.FULL_REPORT_CHAT_TYPE:
            await FullReportChatStateHandler.handle_message(self, chat, message, connections)
        elif chat.chat_type == ChatType.HOMEWORK_CHAT_TYPE:
            await HomeworkChatStateHandler.handle_message(self, chat, message, connections)
        elif chat.chat_type == ChatType.WORK_WITH_FILE_CHAT_TYPE:
            await WorkWithFileChatStateHandler.handle_message(self, chat, message, connections)

    async def init_first_message(self, chat: ChatSchema, connections) -> None:
        """
        При первом сообщении перенаправляет к нужному обработчику.
        """
        if chat.chat_type == ChatType.DIPLOMA_CHAT_TYPE:
            await DiplomaChatStateHandler._first_message_init(chat, connections)
        elif chat.chat_type == ChatType.CONTROL_WORK_CHAT_TYPE:
            await ControlWorkChatStateHandler._first_message_init(chat, connections)
        elif chat.chat_type == ChatType.ESSAY_CHAT_TYPE:
            await EssayChatStateHandler._first_message_init(chat, connections)
        elif chat.chat_type == ChatType.WRITING_CHAT_TYPE:
            await WritingChatStateHandler._first_message_init(chat, connections)
        elif chat.chat_type == ChatType.REPORT_CHAT_TYPE:
            await ReportChatStateHandler._first_message_init(chat, connections)
        elif chat.chat_type == ChatType.FULL_REPORT_CHAT_TYPE:
            await FullReportChatStateHandler._first_message_init(chat, connections)
        elif chat.chat_type == ChatType.HOMEWORK_CHAT_TYPE:
            await HomeworkChatStateHandler._first_message_init(chat, connections)
        elif chat.chat_type == ChatType.WORK_WITH_FILE_CHAT_TYPE:
            await WorkWithFileChatStateHandler._first_message_init(chat, connections)
