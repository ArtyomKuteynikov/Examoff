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
    CONTROL_WORK_CHAT_TYPE = 'CONTROL_WORK_CHAT_TYPE'
    ESSAY_CHAT_TYPE = 'ESSAY_CHAT_TYPE'
    WRITING_CHAT_TYPE = 'WRITING_CHAT_TYPE'
    REPORT_CHAT_TYPE = 'REPORT_CHAT_TYPE'
    FULL_REPORT_CHAT_TYPE = 'FULL_REPORT_CHAT_TYPE'
    HOMEWORK_CHAT_TYPE = 'HOMEWORK_CHAT_TYPE'


class DiplomaChatStateEnum(StrEnum):
    """
    Состояние диалога при заказе дипломной работы.
    ==============================================

    WELCOME_MESSAGE.
        Приветствие + выбор “Приступить к началу работы”;

    ASK_THEME.
        Выбор темы.

    ASK_WORK_SIZE.
        Выбор объема работы в страницах.

    ASK_OTHER_REQUIREMENTS.
        Выбор стандартов/требований к работе.

    ASK_INFORMATION_SOURCE.
        Выбор источников.

    ASK_ANY_INFORMATION.
        Дополнительная информация от пользователя - переход к следующему этапу.

    ASK_ACCEPT_PLAN.
        Вывод плана + выбор “Сгенерировать новый план”/”Перейти к генерации текста”.

    ASK_ACCEPT_TEXT_STRUCTURE.
        Вывод текста + выбор “Сгенерировать новый текст”/”Скачать файл”.

    DIALOG_IS_OVER.
        Заключение - вывод файла + выбор “К выбору категорий”/”Продолжить”.
    """
    WELCOME_MESSAGE = "welcome_message"
    ASK_THEME = "ask_theme"
    ASK_WORK_SIZE = "ask_work_size"
    ASK_OTHER_REQUIREMENTS = "ask_other_requirements"
    ASK_INFORMATION_SOURCE = "ask_information_source"
    ASK_ANY_INFORMATION = "ask_any_information"
    ASK_ACCEPT_PLAN = "ask_accept_plan"
    ASK_ACCEPT_TEXT_STRUCTURE = "ask_accept_text_structure"
    DIALOG_IS_OVER = "dialog_is_over"


class WorkWithFileChatStateEnum(StrEnum):
    """
    Состояние диалога при прикреплении файла.
    =========================================

    WELCOME_MESSAGE.
        Приветствие и "Прикрепить файл".

    FILE_ANALYZED.
        Процессбар загрузки и анализа файлов.

    START_ASKING.
        Любые вопросы по этому файлу.
        Пример: "Кто изобрел машину, описанную во второй главе?"
    """
    WELCOME_MESSAGE = "welcome_message"
    FILE_ANALYZED = "file_analyzed"
    START_ASKING = 'start_asking'


class ControlWorkChatStateEnum(StrEnum):
    """
    Состояние диалога при заказе контрольной работы.
    ================================================

    WELCOME_MESSAGE.
        Приветствие + выбор “Приступить к началу работы”;

    ASK_THEME.
        Выбор темы.

    ASK_WORK_SIZE.
        Выбор объема работы в страницах.

    ASK_OTHER_REQUIREMENTS.
        Выбор стандартов/требований к работе.

    ASK_INFORMATION_SOURCE.
        Выбор источников.

    ASK_ANY_INFORMATION.
        Дополнительная информация от пользователя - переход к следующему этапу.

    ASK_ACCEPT_PLAN.
        Вывод плана + выбор “Сгенерировать новый план”/”Перейти к генерации текста”.

    ASK_ACCEPT_TEXT_STRUCTURE.
        Вывод текста + выбор “Сгенерировать новый текст”/”Скачать файл”.

    DIALOG_IS_OVER.
        Заключение - вывод файла + выбор “К выбору категорий”/”Продолжить”.
    """
    WELCOME_MESSAGE = "welcome_message"
    ASK_THEME = "ask_theme"
    ASK_WORK_SIZE = "ask_work_size"
    ASK_OTHER_REQUIREMENTS = "ask_other_requirements"
    ASK_INFORMATION_SOURCE = "ask_information_source"
    ASK_ANY_INFORMATION = "ask_any_information"
    ASK_ACCEPT_PLAN = "ask_accept_plan"
    ASK_ACCEPT_TEXT_STRUCTURE = "ask_accept_text_structure"
    DIALOG_IS_OVER = "dialog_is_over"


class EssayChatStateEnum(StrEnum):
    """
    Состояние диалога при заказе эссе.
    ==================================

    WELCOME_MESSAGE.
        Приветствие + выбор “Приступить к началу работы”;

    ASK_THEME.
        Выбор темы.

    ASK_WORK_SIZE.
        Выбор объема работы в страницах.

    ASK_OTHER_REQUIREMENTS.
        Выбор стандартов/требований к работе.

    ASK_INFORMATION_SOURCE.
        Выбор источников.

    ASK_ASPECTS_PROBLEM.
        Выбор аспектов проблемы.
        Пример: "Следующий вопрос: какие аспекты проблемы вашей темы вы бы хотели
        осветить. Например, философские социальные, психологические, религиозные и д.р"

    ASK_OPINION.
        Выбор точки зрения.
        Пример: "Хорошо, пропускаем вопрос об аспектах проблемы вашей темы. Следующий вопрос: есть
        ли конкретный угол зрения или тезис, который вы хотели бы поддержать в своем эссе?".

    ASK_WRITING_STYLE.
        Выбор стилистики написания.
        Пример: "Прекрасно! Далее, мне необходимо уточнить стилистику вашей работы. Какая стилистика работы вам
        необходима или предпочтительна? (например: научный, художественный, разговорный и т.д)"

    ASK_ANY_INFORMATION.
        Дополнительная информация от пользователя - переход к следующему этапу.

    ASK_ACCEPT_PLAN.
        Вывод плана + выбор “Сгенерировать новый план”/”Перейти к генерации текста”.

    ASK_ACCEPT_TEXT_STRUCTURE.
        Вывод текста + выбор “Сгенерировать новый текст”/”Скачать файл”.

    DIALOG_IS_OVER.
        Заключение - вывод файла + выбор “К выбору категорий”/”Продолжить”.
    """
    WELCOME_MESSAGE = "welcome_message"
    ASK_THEME = "ask_theme"
    ASK_WORK_SIZE = "ask_work_size"
    ASK_OTHER_REQUIREMENTS = "ask_other_requirements"
    ASK_INFORMATION_SOURCE = "ask_information_source"
    ASK_ASPECTS_PROBLEM = "ask_aspects_problem"
    ASK_OPINION = "ask_opinion"
    ASK_WRITING_STYLE = "ask_writing_style"
    ASK_ANY_INFORMATION = "ask_any_information"
    ASK_ACCEPT_PLAN = "ask_accept_plan"
    ASK_ACCEPT_TEXT_STRUCTURE = "ask_accept_text_structure"
    DIALOG_IS_OVER = "dialog_is_over"


class WritingChatStateEnum(StrEnum):
    """
    Состояние диалога при заказе сочинения.
    =======================================

    WELCOME_MESSAGE.
        Приветствие + выбор “Приступить к началу работы”;

    ASK_THEME.
        Выбор темы.

    ASK_WORK_SIZE.
        Выбор объема работы в страницах.

    ASK_OTHER_REQUIREMENTS.
        Выбор стандартов/требований к работе.

    ASK_INFORMATION_SOURCE.
        Выбор источников.

    ASK_WRITING_STYLE.
        Выбор стилистики написания.
        Пример: "Прекрасно! Далее, мне необходимо уточнить стилистику вашей работы. Какая стилистика работы вам
        необходима или предпочтительна? (например: научный, художественный, разговорный и т.д)"

    ASK_ANY_INFORMATION.
        Дополнительная информация от пользователя - переход к следующему этапу.

    ASK_ACCEPT_TEXT_STRUCTURE.
        Вывод текста + выбор “Сгенерировать новый текст”/”Скачать файл”.

    DIALOG_IS_OVER.
        Заключение - вывод файла + выбор “К выбору категорий”/”Продолжить”.
    """
    WELCOME_MESSAGE = "welcome_message"
    ASK_THEME = "ask_theme"
    ASK_WORK_SIZE = "ask_work_size"
    ASK_OTHER_REQUIREMENTS = "ask_other_requirements"
    ASK_INFORMATION_SOURCE = "ask_information_source"
    ASK_WRITING_STYLE = "ask_writing_style"
    ASK_ANY_INFORMATION = "ask_any_information"
    ASK_ACCEPT_TEXT_STRUCTURE = "ask_accept_text_structure"
    DIALOG_IS_OVER = "dialog_is_over"


class ReportChatStateEnum(StrEnum):
    """
    Состояние диалога при заказе реферата.
    ======================================

    WELCOME_MESSAGE.
        Приветствие + выбор “Приступить к началу работы”;

    ASK_THEME.
        Выбор темы.

    ASK_WORK_SIZE.
        Выбор объема работы в страницах.

    ASK_ASPECTS_ANALYSIS.
        Выбор аспектов для анализа. На каких примерах будет проводиться анализ
        Пример: "Для полноценного исследования темы "Монополия, как понятие и пути изменения власти монополии" мне
        необходимо знать, есть ли конкретные аспекты или примеры монополий, на которые вы хотели бы сосредоточиться,
        например, исторические случаи, современные примеры, отдельные отрасли или географические рынки?"

    ASK_ANALYSIS_TYPE.
        Выбор типа анализа. В каком типе отраслей проводить анализ: в экономическом плане, политическом и т.д.
        Пример: "Отлично, сосредоточимся на современных примерах монополий. Прежде чем я начну писать
        реферат, хотел бы уточнить, какой уровень анализа вам необходим – это должен быть обзор с экономической теорией,
        анти-монопольным законодательством, практическими примерами или вам нужен более углубленный анализ с
        собственными предложениями по изменению власти монополий?"

    ASK_WRITING_STYLE.
        Выбор стилистики написания.
        Пример: "Прекрасно! Далее, мне необходимо уточнить стилистику вашей работы. Какая стилистика работы вам
        необходима или предпочтительна? (например: научный, художественный, разговорный и т.д)"

    ASK_ANY_INFORMATION.
        Дополнительная информация от пользователя - переход к следующему этапу.

    ASK_ACCEPT_TEXT_STRUCTURE.
        Вывод текста + выбор “Сгенерировать новый текст”/”Скачать файл”.

    DIALOG_IS_OVER.
        Заключение - вывод файла + выбор “К выбору категорий”/”Продолжить”.
    """
    WELCOME_MESSAGE = "welcome_message"
    ASK_THEME = "ask_theme"
    ASK_WORK_SIZE = "ask_work_size"
    ASK_ASPECTS_ANALYSIS = "ask_aspects_analysis"
    ASK_ANALYSIS_TYPE = "ask_analysis_type"
    ASK_WRITING_STYLE = "ask_writing_style"
    ASK_ANY_INFORMATION = "ask_any_information"
    ASK_ACCEPT_TEXT_STRUCTURE = "ask_accept_text_structure"
    DIALOG_IS_OVER = "dialog_is_over"


class FullReportChatStateEnum(StrEnum):
    """
    Состояние диалога при заказе доклада.
    =====================================

    WELCOME_MESSAGE.
        Приветствие + выбор “Приступить к началу работы”;

    ASK_THEME.
        Выбор темы.

    ASK_WORK_SIZE.
        Выбор объема работы в страницах.

    ASK_INFORMATION_SOURCE.
        Выбор источников.

    ASK_WRITING_STYLE.
        Выбор стилистики написания.
        Пример: "Прекрасно! Далее, мне необходимо уточнить стилистику вашей работы. Какая стилистика работы вам
        необходима или предпочтительна? (например: научный, художественный, разговорный и т.д)"

    ASK_ANY_INFORMATION.
        Дополнительная информация от пользователя - переход к следующему этапу.

    ASK_ACCEPT_TEXT_STRUCTURE.
        Вывод текста + выбор “Сгенерировать новый текст”/”Скачать файл”.

    DIALOG_IS_OVER.
        Заключение - вывод файла + выбор “К выбору категорий”/”Продолжить”.
    """
    WELCOME_MESSAGE = "welcome_message"
    ASK_THEME = "ask_theme"
    ASK_WORK_SIZE = "ask_work_size"
    ASK_INFORMATION_SOURCE = "ask_information_source"
    ASK_WRITING_STYLE = "ask_writing_style"
    ASK_ANY_INFORMATION = "ask_any_information"
    ASK_ACCEPT_TEXT_STRUCTURE = "ask_accept_text_structure"
    DIALOG_IS_OVER = "dialog_is_over"


class HomeworkChatStateEnum(StrEnum):
    """
    Состояние диалога при заказе домашнего задания.
    ===============================================

    WELCOME_MESSAGE.
        Приветствие + выбор “Приступить к началу работы”;

    ASK_THEME.
        Выбор темы.

    ASK_WORK_SIZE.
        Выбор объема работы в страницах.

    ASK_OTHER_REQUIREMENTS.
        Выбор стандартов/требований к работе.

    ASK_INFORMATION_SOURCE.
        Выбор источников.

    ASK_ANY_INFORMATION.
        Дополнительная информация от пользователя - переход к следующему этапу.

    ASK_ACCEPT_PLAN.
        Вывод плана + выбор “Сгенерировать новый план”/”Перейти к генерации текста”.

    ASK_ACCEPT_TEXT_STRUCTURE.
        Вывод текста + выбор “Сгенерировать новый текст”/”Скачать файл”.

    DIALOG_IS_OVER.
        Заключение - вывод файла + выбор “К выбору категорий”/”Продолжить”.
    """
    WELCOME_MESSAGE = "welcome_message"
    ASK_THEME = "ask_theme"
    ASK_WORK_SIZE = "ask_work_size"
    ASK_OTHER_REQUIREMENTS = "ask_other_requirements"
    ASK_INFORMATION_SOURCE = "ask_information_source"
    ASK_ANY_INFORMATION = "ask_any_information"
    ASK_ACCEPT_PLAN = "ask_accept_plan"
    ASK_ACCEPT_TEXT_STRUCTURE = "ask_accept_text_structure"
    DIALOG_IS_OVER = "dialog_is_over"
