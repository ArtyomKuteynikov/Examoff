import os
from typing import List, Optional

import anthropic
from dotenv import load_dotenv

from ai_module.schemas.message import Message, messages_to_anthropic_format

load_dotenv()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY is empty"))


def create_anthropic_message(
        model: str,
        system_message: str,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
):
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_message,
        messages=messages_to_anthropic_format(messages),
    )


client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, world"}
    ]
)
