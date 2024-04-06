"""Module for enums."""
from enum import Enum


class StrEnum(str, Enum):  # noqa: WPS600
    """Base enum."""


class GPT_Model(StrEnum):
    """
    Enum для списка моделей OpenAI.
    Список моделей: https://platform.openai.com/docs/models/overview.
    """
    GPT_3_5_TURBO_0613 = "gpt-3.5-turbo-0613"
    GPT_3_5_TURBO_0125 = "gpt-3.5-turbo-0125"
    GPT_3_5_TURBO_16K_0613 = "gpt-3.5-turbo-16k-0613"
    GPT_4_0314 = "gpt-4-0314"
    GPT_4_32K_0314 = "gpt-4-32k-0314"
    GPT_4_0613 = "gpt-4-0613"
    GPT_4_32K_0613 = "gpt-4-32k-0613"


class Role_Message(StrEnum):
    """
    Enum для возможных ролей в сообщении.
    https://platform.openai.com/docs/api-reference/chat/create
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
