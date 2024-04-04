"""
Dataclass Completion.
"""
from typing import Literal

from pydantic import BaseModel

from ai_module.schemas.enums import Role_Message


class Completion(BaseModel):
    """
    Обработчик response Chat Completions.
    =====================================

    Class properties
    ----------------

    model: str
        Модель OpenAI.
        Example: "gpt-3.5-turbo"

    content: str
        Текст сообщения.
        Example: 'Hello! How can I assist you today with translating corporate jargon into plain English?'

    role: str
        Автор сообщения.

    prompt_tokens: int
        Цена prompt, выраженная в tokens.

    completion_tokens: int
        Цена completion, выраженная в tokens.

    total_tokens: int
        total_tokens = prompt_tokens + completion_tokens
    """
    model: str
    content: str
    role: Literal[Role_Message.ASSISTANT] = "assistant"
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
