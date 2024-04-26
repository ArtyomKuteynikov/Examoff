"""Обработка сообщения пользователя с использованием ai."""
import json
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
from test_case_from_prompt_engineer import promts

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))


def handle_question_ask_work_size(user_answer):
    messages = [
        SystemMessage(content=promts.GENERAL_PROMPT),
        UserMessage(content=promts.ASK_WORK_SIZE.format(USER_ANSWER=user_answer)),
    ]
    completion = client.chat.completions.create(
        model=GPT_Model.GPT_4_TURBO,
        messages=messages_to_openai_format(messages),
        response_format={"type": "json_object"},
    )

    try:
        answer = json.loads(completion.choices[0].message.content)
        if int(answer['Минимальный объем символов']) and int(answer['Минимальный объем символов']):
            return answer

    except Exception:
        return None
