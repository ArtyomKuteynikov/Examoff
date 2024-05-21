"""Обработчик состояний чата для заказа диплома."""
import json
import os
import uuid

from dotenv import load_dotenv
from openai import AsyncOpenAI

from gateway.chat.dependens.answers import send_message_and_change_state, send_free_sate_message_in_websockets, \
    open_free_sate_message_in_websockets, create_system_message_in_db, change_chat_state
from gateway.config.database import async_session_maker
from gateway.db.messages.repo import MessageRepo
from gateway.resources.chat_state_strings import free_state_state_strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import FreeStateChatStateEnum
from gateway.schemas.message import MessageSchema

load_dotenv()
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))


class FreeStateChatStateHandler:
    """
    Обработчик состояния для свободного режима.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            FreeStateChatStateEnum.CIRCLE: self._free_state_circle,
        }

    @staticmethod
    async def _first_message_init(chat: ChatSchema, connections) -> None:
        """
        Обработчик первого подключения по websocket.
        Действие выполняется, когда только создается чат с пользователем и инициализируется
        первое подключение по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=free_state_state_strings.FREE_STATE_INIT_MESSAGE,
            state=FreeStateChatStateEnum.CIRCLE,
        )

    async def handle_message(self, chat: ChatSchema, message: MessageSchema, connections) -> None:
        """
        Определяет какое состояние чата и вызывает соответствующий метод.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        method = self.state_methods.get(chat.chat_state)
        if method:
            await method(chat, message, connections)

    @staticmethod
    async def _free_state_circle(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `CIRCLE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        async with async_session_maker() as session:
            message_repo = MessageRepo(session)
            bd_messages = await message_repo.get_messages_by_attributes({'chat_id': chat.id})

            for mes in bd_messages[-9:]:
                if mes.sender_id == 1:
                    messages.append(
                        {"role": "assistant", "content": mes.text}
                    )
                else:
                    messages.append(
                        {"role": "user", "content": mes.text}
                    )

        completion = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            stream=True
        )

        message_to_send = ''
        await open_free_sate_message_in_websockets(connections, chat)
        async for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                message_to_send += chunk.choices[0].delta.content
                await send_free_sate_message_in_websockets(
                    connections,
                    chat,
                    chunk.choices[0].delta.content,
                    chunk.choices[0].finish_reason
                )
            else:
                await send_free_sate_message_in_websockets(
                    connections,
                    chat,
                    '',
                    chunk.choices[0].finish_reason
                )

        await create_system_message_in_db(chat, message_to_send)
        await change_chat_state(chat, FreeStateChatStateEnum.CIRCLE)
