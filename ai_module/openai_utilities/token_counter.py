"""
Подсчет количество токенов, используемых для запроса к openai.
Источник: https://platform.openai.com/docs/guides/text-generation/managing-tokens
"""

import os
import tiktoken

from typing import List
from openai import OpenAI

from ai_module.schemas.enums import GPT_Model
from ai_module.schemas.message import Message, messages_to_openai_format, SystemMessage, UserMessage


def num_tokens_from_messages(messages: List[Message], model: str = "gpt-3.5-turbo-0613") -> int:
    """
    Возвращает количество токенов, подсчитанных для сообщений.

    :param messages: Список сообщений для отправки.
    :param model: Название модели.
    :return: Количество токенов.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in GPT_Model._value2member_map_:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai
            -python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in [message.dict(exclude_none=True) for message in messages]:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def main():
    """
    Функция для запуска файла напрямую. Является примером для тестирования.
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))

    example_messages = [
        SystemMessage(
            content="You are a helpful, pattern-following assistant that translates corporate jargon into plain "
                    "English."
        ),
        UserMessage(content="Hello.")
    ]

    models = ['gpt-4-0613']
    for model in models:
        print(model)
        # example token count from the function defined above
        print(
            f"{num_tokens_from_messages(example_messages, model)} prompt tokens counted by num_tokens_from_messages().")
        # example token count from the OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages_to_openai_format(example_messages),
            temperature=0,
            max_tokens=1
        )
        print(f'{response.usage.prompt_tokens} prompt tokens counted by the OpenAI API.')


if __name__ == "__main__":
    main()
