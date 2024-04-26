"""Обработка сообщения пользователя с использованием ai."""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from ai_module.schemas.enums import GPT_Model
from ai_module.schemas.message import UserMessage, SystemMessage, messages_to_openai_format
from gateway.config.database import async_session_maker
from gateway.db.messages.repo import MessageRepo
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import ChatTypeTranslate
from test_case_from_prompt_engineer import promts

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))


async def generate_plan_via_chat(chat: ChatSchema):
    async with async_session_maker() as session:
        message_repo = MessageRepo(session)
        messages = await message_repo.get_messages_by_attributes({'chat_id': chat.id})

        filtered_messages = [message for message in messages if message.response_specific_state is not None]
        messages = {}
        for message in filtered_messages:
            messages[message.response_specific_state] = message
        work_size = eval(messages['JSON_WORK_SIZE'].text)
        theme = messages['ask_theme'].text
        work_type = ChatTypeTranslate[chat.chat_type].value
        return generate_plan(
            theme=theme,
            work_type=work_type,
            work_size_min=work_size['Минимальный объем символов'],
            work_size_max=work_size['Максимальный объем символов'],
        )


def generate_plan(theme, work_type, work_size_min, work_size_max, func_count=0):
    if func_count == 10:
        return None

    user_prompt = promts.PLAN_PROMPT.format(
        THEME=theme,
        TYPE=work_type,
        WORK_SIZE_MIN=work_size_min,
        WORK_SIZE_MAX=work_size_max,
    )
    messages = [
        SystemMessage(content=promts.GENERAL_PROMPT),
        UserMessage(content=user_prompt),
    ]

    completion = client.chat.completions.create(
        model=GPT_Model.GPT_4_TURBO,
        messages=messages_to_openai_format(messages),
        response_format={"type": "json_object"},
    )

    try:
        plan = json.loads(completion.choices[0].message.content)

        elements_counter = 0
        for element in plan:
            if element.startswith("Element-"):
                elements_counter += 1
                if not plan[element]['Name']:
                    raise
                if not plan[element]['Character capacity']:
                    raise

        if elements_counter < 3:
            raise

        return plan
    except Exception:
        return generate_plan(theme, work_type, work_size_min, work_size_max, func_count + 1)


async def get_work_plan_from_db(chat: ChatSchema):
    async with async_session_maker() as session:
        message_repo = MessageRepo(session)
        messages = await message_repo.get_messages_by_attributes({'chat_id': chat.id})

        filtered_messages = [message for message in messages if message.response_specific_state is not None]
        messages = {}
        for message in filtered_messages:
            messages[message.response_specific_state] = message

        plan = messages['JSON_PLAN'].text
        return plan
