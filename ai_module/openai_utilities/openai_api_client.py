"""
Модуль для создания запросов к API OpenAI.
"""
import os
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from ai_module.schemas.completion import Completion
from ai_module.schemas.message import Message, messages_to_openai_format

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))


def create_openai_completion(
        model: str,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
) -> Completion:
    """
    Создание request диалога к OpenAI. На выходе ожидается сгенерированный текст с его метаданными.
    Список всех доступных параметров для добавления: https://platform.openai.com/docs/api-reference/chat/create

    :param model: Имя модели.
    :param messages: Список сообщений (контекст чата).
    :param max_tokens: Максимальное количество токенов, используемое для генерации.
    :param temperature: Доступные значения от 0 до 2.
        Более высокие значения, например 0,8, сделают выходные данные более случайными, в то время как более низкие
        значения, например 0,2, сделают их более целенаправленными и детерминированными.
    :return: Dataclass Completion.
    """

    response_completion = client.chat.completions.create(
        model=model,
        messages=messages_to_openai_format(messages),
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return Completion(
        model=response_completion.model,
        content=response_completion.choices[0].message.content,
        prompt_tokens=response_completion.usage.prompt_tokens,
        completion_tokens=response_completion.usage.completion_tokens,
        total_tokens=response_completion.usage.total_tokens,
    )
