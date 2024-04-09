"""Chat repo."""
from typing import List, Dict, Any

from sqlalchemy import select

from gateway.db.crud import CRUD
from gateway.db.sqlalchemy_db import AsyncSession
from gateway.db.chats.models import ChatModel
from gateway.schemas.chat import ChatSchema, ChatInCreationSchema


class ChatRepo:
    def __init__(self, session: AsyncSession):
        """Initialize repo with CRUD."""
        self._session = session
        self._crud = CRUD(session=session, cls_model=ChatModel)

    async def create_chat(self, chat_in_creation: ChatInCreationSchema) -> ChatSchema:
        """Create a new Chat."""
        chat_row = await self._crud.create(
            model_data={
                "chat_state": chat_in_creation.chat_state,
                "chat_type": chat_in_creation.chat_type,
            }
        )
        return await self.get_chat_by_id(chat_row.id)

    async def get_chat_by_id(self, chat_id: int) -> ChatSchema:
        """Get chat by id."""
        row = await self._session.execute(
            select(ChatModel).where(ChatModel.id == chat_id)
        )
        chat = row.scalars().unique().first()
        return ChatSchema.model_validate(chat)

    async def get_chats_by_attributes(self, attributes: Dict[str, Any]) -> List[ChatSchema]:
        """
        Получение чатов по заданным атрибутам.

        :param attributes: Словарь атрибутов и их значений для фильтрации. Пример: {"chat_type": "DIPLOMA_CHAT_TYPE"}
        :return: Список чатов, соответствующих заданным атрибутам.
        """
        query = select(ChatModel)
        for attribute, value in attributes.items():
            query = query.where(getattr(ChatModel, attribute) == value)

        result = await self._session.execute(query)
        chats = result.scalars().all()
        return [ChatSchema.model_validate(chat) for chat in chats]

    async def update_chat(self, chat: ChatSchema) -> None:
        """Update chat state"""
        await self._crud.update(
            model_data={
                "chat_state": chat.chat_state,
                "chat_type": chat.chat_type,
            },
            pkey_val=chat.id,
        )