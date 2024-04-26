"""Обработка сообщения пользователя с использованием ai."""
import os

from dotenv import load_dotenv
from openai import OpenAI

from ai_module.schemas.enums import GPT_Model
from ai_module.schemas.message import UserMessage, SystemMessage, AssistantMessage, messages_to_openai_format
from gateway.resources.strings import PLAN_STRUCTURE_MESSAGE
from gateway.schemas.enums import DiplomaChatStateEnum
from gateway.config.database import get_db
from gateway.db.messages.repo import MessageRepo
from gateway.resources import strings

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))


def process_user_message_on_welcome_message_status(user_answer: str) -> str | None:
    pass


def process_user_message_on_ask_theme_status(user_answer: str):
    pass


def process_user_message_on_ask_work_size_status(user_answer: str) -> str | None:
    """
    Обработка сообщения пользователя при помощи ai для статуса `ASK_WORK_SIZE`.
    Определяет верно ли пользователь указал объем:
        1: Пользователь указал объем верно;
        None: Пользователь не определился с выбором.

    :param user_answer: Сообщение пользователя.
    """
    messages = [
        SystemMessage(content=strings.SYSTEM_CONTEXT_DIPLOMA_ASK_WORK_SIZE),
        AssistantMessage(content=strings.DIPLOMA_ASK_WORK_SIZE),  # todo Заменить на промт от промтовика.
        UserMessage(content=user_answer + strings.END_OF_USER_MESSAGE_DIPLOMA_ASK_WORK_SIZE),
    ]
    completion = client.chat.completions.create(
        model=GPT_Model.GPT_3_5_TURBO_0125,
        messages=messages_to_openai_format(messages),
    )
    try:
        return 1 if int(completion.choices[0].message.content) == 1 else None
    except TypeError:
        return None


async def generate_user_plan(chat_id) -> str:
    """
    Генерация плана. Следует перенести в другой модуль.
    """
    # todo Сделать нормальную генерацию плана.
    return PLAN_STRUCTURE_MESSAGE

    async for session in get_db():
        repo = MessageRepo(session)
        messages = await repo.get_messages_by_attributes({"chat_id": chat_id})

        filtered_messages = [message for message in messages if message.response_specific_state is not None]
        my_dict = {}
        for message in filtered_messages:
            my_dict[message.response_specific_state] = message

        plan_request = (
            f"Привет, сгенерируй мне план по дипломной работе с темой `{my_dict[DiplomaChatStateEnum.ASK_THEME]}`.\n"
            f"Где объем работы: {my_dict[DiplomaChatStateEnum.ASK_WORK_SIZE]}\n"
            f"Требования по работе: {my_dict[DiplomaChatStateEnum.ASK_OTHER_REQUIREMENTS]}\n"
            f"Источники информации: {my_dict[DiplomaChatStateEnum.ASK_INFORMATION_SOURCE]}\n"
            f"Дополнительная информация: {my_dict[DiplomaChatStateEnum.ASK_ANY_INFORMATION]}\n"
            "___\n"
            "Введение и вывод - это не главы, но всё равно их добавь в план без цифры."
            "Напиши мне план со структурой и ничего лишнего:\n"
            "1.\n"
            "2.\n"
            "3.\n"

            "Только план, без любых вводных конструкций, и не говори мне конечно."
        )

        request_to_nlp = [
            SystemMessage(content=strings.SYSTEM_CONTEXT_HELPER_DIPLOMA_ASK_ACCEPT_PLAN),
            UserMessage(content=plan_request),
        ]
        completion = client.chat.completions.create(
            model=GPT_Model.GPT_3_5_TURBO_0125,
            messages=messages_to_openai_format(request_to_nlp),
            temperature=1.8
        )
        return completion.choices[0].message.content


def process_user_message_on_ask_accept_plan_status(user_answer: str) -> str | None:
    """
    Обработка сообщения пользователя при помощи ai для статуса `ASK_ACCEPT_PLAN`.
    Определяет согласен ли пользователь с предложенным планом:
        1: Пользователь согласен с планом;
        None: Пользователю план не понравился.

    :param user_answer: Сообщение пользователя.
    """
    messages = [
        SystemMessage(content=strings.SYSTEM_CONTEXT_DIPLOMA_ASK_ACCEPT_PLAN),
        AssistantMessage(content=strings.DIPLOMA_ASK_ACCEPT_PLAN),
        UserMessage(content=user_answer + strings.END_OF_USER_MESSAGE_DIPLOMA_ASK_ACCEPT_PLAN),
    ]
    completion = client.chat.completions.create(
        model=GPT_Model.GPT_3_5_TURBO_0125,
        messages=messages_to_openai_format(messages),
    )
    try:
        return 1 if int(completion.choices[0].message.content) == 1 else None
    except TypeError:
        return None
