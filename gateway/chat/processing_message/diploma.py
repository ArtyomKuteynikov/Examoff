import os
from pprint import pprint

from dotenv import load_dotenv
from openai import OpenAI

from ai_module.schemas.enums import GPT_Model
from ai_module.schemas.message import UserMessage, SystemMessage, AssistantMessage, messages_to_openai_format
from gateway.resources import strings

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))


def process_user_message_on_welcome_message_status(user_answer: str):
    messages = [
        SystemMessage(content=strings.SYSTEM_CONTEXT_DIPLOMA_WELCOME_MESSAGE),
        AssistantMessage(content=strings.DIPLOMA_WELCOME_MESSAGE),
        UserMessage(content=user_answer + strings.END_OF_USER_MESSAGE_DIPLOMA_WELCOME_MESSAGE),
    ]
    completion = client.chat.completions.create(
        model=GPT_Model.GPT_3_5_TURBO_0125,
        messages=messages_to_openai_format(messages),
    )
    try:
        return int(completion.choices[0].message.content)
    except TypeError:
        return 0
