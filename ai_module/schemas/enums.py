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


class Claude_Model(StrEnum):
    """
    Enum для списка моделей Claude.
    """
    CLAUDE_3_OPUS_20240229 = "claude-3-opus-20240229",
    CLAUDE_3_SONNET_20240229 = "claude-3-sonnet-20240229",
    CLAUDE_3_HAIKU_20240307 = "claude-3-haiku-20240307",
    CLAUDE_2_1 = "claude-2.1",
    CLAUDE_2_0 = "claude-2.0",
    CLAUDE_INSTANT_1_2 = "claude-instant-1.2",


class Role_Message(StrEnum):
    """
    Enum для возможных ролей в сообщении.
    https://platform.openai.com/docs/api-reference/chat/create
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
