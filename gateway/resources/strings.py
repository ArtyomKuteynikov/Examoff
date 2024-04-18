"""Text and templates for messages."""

## Report States
REPORT_WELCOME_MESSAGE = (
    "REPORT_WELCOME_MESSAGE"
)
REPORT_ASK_THEME = (
    "REPORT_ASK_THEME"
)
REPORT_ASK_WORK_SIZE = (
    "REPORT_ASK_WORK_SIZE"
)
REPORT_ASK_ASPECTS_ANALYSIS = (
    "REPORT_ASK_ASPECTS_ANALYSIS"
)
REPORT_ASK_ANALYSIS_TYPE = (
    "REPORT_ASK_ANALYSIS_TYPE"
)
REPORT_ASK_WRITING_STYLE = (
    "REPORT_ASK_WRITING_STYLE"
)
REPORT_ASK_ANY_INFORMATION = (
    "REPORT_ASK_ANY_INFORMATION"
)
REPORT_ASK_ACCEPT_TEXT_STRUCTURE = (
    "REPORT_ASK_ACCEPT_TEXT_STRUCTURE"
)

## Full Report States
FULL_REPORT_WELCOME_MESSAGE = (
    "FULL_REPORT_WELCOME_MESSAGE"
)
FULL_REPORT_ASK_THEME = (
    "FULL_REPORT_ASK_THEME"
)
FULL_REPORT_ASK_WORK_SIZE = (
    "FULL_REPORT_ASK_WORK_SIZE"
)
FULL_REPORT_ASK_INFORMATION_SOURCE = (
    "FULL_REPORT_ASK_INFORMATION_SOURCE"
)
FULL_REPORT_ASK_WRITING_STYLE = (
    "FULL_REPORT_ASK_WRITING_STYLE"
)
FULL_REPORT_ASK_ANY_INFORMATION = (
    "FULL_REPORT_ASK_ANY_INFORMATION"
)
FULL_REPORT_ASK_ACCEPT_TEXT_STRUCTURE = (
    "FULL_REPORT_ASK_ACCEPT_TEXT_STRUCTURE"
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
    "Введение"
    "Глава 1. Основные положения ликвидации юридических лиц"
    "1.1. Основания и способы ликвидации юридических лиц."
    "1.2. Ликвидация вследствие признания организации (юридического лица) банкротом."
    "Глава 2. Порядок ликвидации"
    "2.1. Процедура ликвидации юридического лица."
    "2.2. Выплаты денежных сумм кредиторам. Завершение ликвидации."
    "Глава 3. Проблемные вопросы ликвидации юридических лиц"
    "3.1. Новеллы в ликвидации юридических лиц"
    "3.2. Основные проблемы при ликвидации юридических лиц."
    "Заключение"
    "Список используемой литературы"
)
