"""Обработчик состояний чата для работы с микрофоном."""
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from gateway.chat.dependens.answers import send_message_and_change_state

from gateway.resources.chat_state_strings import micro_state_strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import MicroChatStateEnum
from gateway.schemas.message import MessageSchema

load_dotenv()


class MicroChatStateHandler:
    """
    Обработчик состояния для работы с микрофоном.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            MicroChatStateEnum.FIRST_STATE: self._micro_first_state,
            MicroChatStateEnum.SECOND_STATE: self._micro_second_state,
            # ToDo Сюда добавлять новые состояния
        }
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))

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
            message_text=micro_state_strings.MICRO_WELCOME_STATE_MESSAGE,
            state=MicroChatStateEnum.WELCOME_STATE,
        )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=micro_state_strings.MICRO_FIRST_STATE_MESSAGE,
            state=MicroChatStateEnum.FIRST_STATE,
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
    async def _micro_first_state(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `FIRST_STATE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=micro_state_strings.MICRO_SECOND_STATE_MESSAGE,
            state=MicroChatStateEnum.SECOND_STATE,
        )

    async def _micro_second_state(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `FIRST_STATE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        messages = [
            {'role': 'system', 'content': 'You are helpful assistant.'},
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hello! How are you?'}
        ]
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
        )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=response.choices[0].message.content,
            state=MicroChatStateEnum.FIRST_STATE,
        )
