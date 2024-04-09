"""Module for enums."""
from enum import Enum


class StrEnum(str, Enum):  # noqa: WPS600
    """Base enum."""


class WebsocketMessageType(StrEnum):
    """
    Enum возможных типов сообщений по websocket.
    ============================================

    USER_MESSAGE.
        Сообщение, отправленное от пользователя.

    SYSTEM_MESSAGE.
        Сообщение, отправленное от backend.

    USER_MESSAGE_FROM_OTHER_SOCKET.
        Сообщение, отправленное от пользователя.
        Дублирует информацию для других websocket соединений.
    """
    USER_MESSAGE = "user_message"
    SYSTEM_MESSAGE = "system_message"
    USER_MESSAGE_FROM_OTHER_SOCKET = "user_message_from_other_socket"


class ChatType(StrEnum):
    DIPLOMA_CHAT_TYPE = "DIPLOMA_CHAT_TYPE"


class DiplomaChatStateEnum(StrEnum):
    """
    Состояние диалога при заказе дипломной работы
    """
    # Бот спрашивает: Прикрепить файл или приступить к написанию работы
    WELCOME_MESSAGE = "welcome_message"

    # Бот спрашивает: Какая тема вашей дипломной работы
    ASK_THEME = "ask_theme"

    # Бот спрашивает: Какой объем работы
    ASK_WORK_SIZE = "ask_work_size"

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
