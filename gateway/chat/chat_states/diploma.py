"""Module for enums."""
from enum import Enum, auto


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

    def handle_message(self, chat_state: str):
        method = self.state_methods.get(chat_state)
        if method:
            method()

    def _diploma_welcome_message(self):
        print('_diploma_welcome_message')

    def _diploma_ask_theme(self):
        print('_diploma_ask_theme')

    def _diploma_ask_page_number(self):
        print('_diploma_ask_page_number')

    def _diploma_ask_other_requirements(self):
        print('_diploma_ask_other_requirements')

    def _diploma_ask_information_source(self):
        print('_diploma_ask_information_source')

    def _diploma_ask_any_information(self):
        print('_diploma_ask_any_information')

    def _diploma_ask_accept_plan(self):
        print('_diploma_ask_accept_plan')

    def _diploma_ask_accept_text_structure(self):
        print('_diploma_ask_accept_text_structure')

    def _diploma_dialog_is_over(self):
        print('_diploma_dialog_is_over')
