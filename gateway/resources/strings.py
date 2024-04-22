"""Text and templates for messages."""
from typing import Any, Protocol, cast

from mako.lookup import TemplateLookup


class FormatTemplate(Protocol):
    """
    Protocol for correct templates typing.

    Allow use format() instead of render() method that needed to maintain consistency
    with regular string formatting.
    """

    def format(self, **kwargs: Any) -> str:  # noqa: WPS125 A003
        """Render template."""


class TemplateFormatterLookup(TemplateLookup):
    """Represent a collection of templates from the local filesystem."""

    def get_template(self, uri: str) -> FormatTemplate:
        """Cast default mako template to FormatTemplate."""

        def _format(**kwargs: Any) -> str:  # noqa: WPS430
            return template.render(**kwargs).rstrip()

        template = super().get_template(uri)
        template.format = _format  # noqa: WPS125
        return cast(FormatTemplate, template)


lookup = TemplateFormatterLookup(
    directories=["gateway/resources/templates"],
    input_encoding="utf-8",
    strict_undefined=True,
)

## HomeWork States
HOMEWORK_WELCOME_MESSAGE = (
    "HOMEWORK_WELCOME_MESSAGE"
)
HOMEWORK_ASK_THEME = (
    "HOMEWORK_ASK_THEME"
)
HOMEWORK_ASK_WORK_SIZE = (
    "HOMEWORK_ASK_WORK_SIZE"
)
HOMEWORK_ASK_OTHER_REQUIREMENTS = (
    "HOMEWORK_ASK_OTHER_REQUIREMENTS"
)
HOMEWORK_ASK_INFORMATION_SOURCE = (
    "HOMEWORK_ASK_INFORMATION_SOURCE"
)
HOMEWORK_ASK_ANY_INFORMATION = (
    "HOMEWORK_ASK_ANY_INFORMATION"
)
HOMEWORK_ASK_ACCEPT_PLAN = (
    "HOMEWORK_ASK_ACCEPT_PLAN"
)
HOMEWORK_ASK_ACCEPT_TEXT_STRUCTURE = (
    "HOMEWORK_ASK_ACCEPT_TEXT_STRUCTURE"
)

## WorkWithFile States
WORK_WITH_FILE_WELCOME_MESSAGE = (
    "WORK_WITH_FILE_WELCOME_MESSAGE"
)
WORK_WITH_FILE_FILE_ANALYZED = (
    "WORK_WITH_FILE_FILE_ANALYZED"
)
WORK_WITH_FILE_START_ASKING = (
    "WORK_WITH_FILE_START_ASKING"
)

# OpenAI context messages
## Diploma
### WELCOME_MESSAGE
SYSTEM_CONTEXT_DIPLOMA_WELCOME_MESSAGE = (
    "У тебя только три варианта ответа: 0, 1, 2. Я от тебя ожиданию в ответе только один символ."
    "Дальше тебе будет представлена ситуация, где пользователю задают вопрос: прикрепить файл или ответить на "
    "Вопросы в чате. "
    "Если содержание его сообщения значит, что он готов ответить на вопросы в чате, тогда ответь мне сообщением `1`. "
    "Если содержание его сообщения значит, что он готов прикрепить файл, тогда ответь мне сообщением `2`. "
    "Если содержание ничего не значит, либо он не заинтересован ответить на вопрос, тогда ответь `0`. "
    "Повторюсь, ты должен ответить только одним символом!"
)
END_OF_USER_MESSAGE_DIPLOMA_WELCOME_MESSAGE = (
    "\n___\n"
    "Напоминаю, у тебя только три варианта ответа: 0, 1, 2. Я от тебя ожиданию в ответе только один символ. "
    "Если моё сообщения значит, что я готов ответить на вопросы в чате, тогда ответь мне сообщением `1`. "
    "Если моё сообщения значит, что я готов прикрепить файл, тогда ответь мне сообщением `2`. "
    "Если содержание моего сообщения ничего не значит, либо я не заинтересован ответить на вопрос, тогда ответь `0`. "
    "Повторюсь, ты должен ответить только одним символом!"
)
### ASK_THEME -
### ASK_WORK_SIZE
SYSTEM_CONTEXT_DIPLOMA_ASK_WORK_SIZE = (
    "У тебя только 2 варианта ответа: 0, 1. Я от тебя ожиданию в ответе только один символ. "
    "Дальше тебе будет представлена ситуация, где пользователю задают вопрос: какой объем работы нужен? "
    "Если в его сообщении четкое определение объема работы, тогда ответь мне сообщением `1` "
    "Если содержание сообщения не характеризует объем работы, тогда ответь `0`. "
)
END_OF_USER_MESSAGE_DIPLOMA_ASK_WORK_SIZE = (
    "\n___\n"
    "Напоминаю, у тебя только 2 варианта ответа: 0, 1. Я от тебя ожиданию в ответе только один символ. "
    "Если моё сообщение определяет объем работы, тогда ответь мне сообщением `1`. "
    "Если моё сообщение не характеризует объем работы, тогда ответь `0`. "
    "Повторюсь, ты должен ответить только одним символом!"
)
### ASK_ACCEPT_PLAN
SYSTEM_CONTEXT_HELPER_DIPLOMA_ASK_ACCEPT_PLAN = (
    "Ты преподаватель, который консультирует и помогает студентам."
)
SYSTEM_CONTEXT_DIPLOMA_ASK_ACCEPT_PLAN = (
    "У тебя только 2 варианта ответа: 0, 1. Я от тебя ожиданию в ответе только один символ. "
    "Дальше тебе будет представлена ситуация, где пользователю задают вопрос: подходит ли ему план работ?"
    "Если он говорит, что план работ ему подходит, тогда ответь мне сообщением `1` "
    "Если содержание сообщения не характеризует, что ему подходит план данной работы, тогда ответь `0`. "
)
END_OF_USER_MESSAGE_DIPLOMA_ASK_ACCEPT_PLAN = (
    "\n___\n"
    "Напоминаю, у тебя только 2 варианта ответа: 0, 1. Я от тебя ожиданию в ответе только один символ. "
    "Если моё сообщение определяет, что план работ мне подходит, тогда ответь мне сообщением `1` "
    "Если моё содержание сообщения не характеризует, что мне подходит план данной работы, тогда ответь `0`. "
    "Повторюсь, ты должен ответить только одним символом!"
)

# Other
NOT_YET_MESSAGE = (
    "Данный пункт не готов"
)
NOT_YET_MESSAGE2 = (
    "Ты мой личный помощник."
)
PLAN_STRUCTURE_MESSAGE = (
    "Введение\n"
    "Глава 1. Основные положения ликвидации юридических лиц\n"
    "1.1. Основания и способы ликвидации юридических лиц.\n"
    "1.2. Ликвидация вследствие признания организации (юридического лица) банкротом.\n"
    "Глава 2. Порядок ликвидации\n"
    "2.1. Процедура ликвидации юридического лица.\n"
    "2.2. Выплаты денежных сумм кредиторам. Завершение ликвидации.\n"
    "Глава 3. Проблемные вопросы ликвидации юридических лиц\n"
    "3.1. Новеллы в ликвидации юридических лиц\n"
    "3.2. Основные проблемы при ликвидации юридических лиц.\n"
    "Заключение\n"
    "Список используемой литературы\n"
)
