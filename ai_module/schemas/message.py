"""
Dataclass Message.
"""

from typing import List, Literal
from pydantic import BaseModel

from ai_module.schemas.enums import Role_Message


class Message(BaseModel):
    """
    Родительский класс сообщения для использования в Chat Completions.
    ==================================================================

    Class properties
    ----------------

    role: str
        Автор сообщения.
        Validation: Может быть только: `system` | `user` | `assistant`.

    content: str
        Текст сообщения.
        Example: "You are a helpful, pattern-following assistant that translates corporate jargon into English."
    """
    role: Literal[Role_Message.SYSTEM, Role_Message.USER, Role_Message.ASSISTANT]
    content: str


class SystemMessage(Message):
    """
    Системное сообщение используется для объявления персонажа, от лица которого будет генерироваться текст.
    Example: "You will be provided with a pair of articles (delimited with XML tags) about the same topic."
    """
    role: Literal[Role_Message.SYSTEM] = "system"


class UserMessage(Message):
    """
    Сообщение от пользователя.
    """
    role: Literal[Role_Message.USER] = "user"


class AssistantMessage(Message):
    """
    Сообщение, что было сгенерировано ассистентом.
    """
    role: Literal[Role_Message.ASSISTANT] = "assistant"


def messages_to_openai_format(messages: List[Message]) -> list[dict[str, str]]:
    """
    Приводит в единый формат для запроса к OpenAI API.

    :param messages: Сообщения/Контекстный запрос.
    :return: Список по примеру:
    [
        {
            "role": "system",
            "content": "You are a helpful, pattern-following assistant that translates corporate jargon into English.",
        },
    ]
    """
    return [message.model_dump() for message in messages]
