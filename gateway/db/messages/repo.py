"""Message repo."""
from typing import List, Dict, Any

from sqlalchemy import select

from gateway.db.crud import CRUD
from gateway.db.sqlalchemy_db import AsyncSession
from gateway.db.messages.models import MessageModel
from gateway.schemas.message import MessageSchema, MessageInCreationSchema


class MessageRepo:
    def __init__(self, session: AsyncSession):
        """Initialize repo with CRUD."""
        self._session = session
        self._crud = CRUD(session=session, cls_model=MessageModel)

    async def create_message(self, message_in_creation: MessageInCreationSchema) -> MessageSchema:
        """Create a new Message."""
        message_row = await self._crud.create(
            model_data={
                "chat_id": message_in_creation.chat_id,
                "text": message_in_creation.text,
                "sender_id": message_in_creation.sender_id,
                "created_at": message_in_creation.created_at,
                "response_specific_state": message_in_creation.response_specific_state,
                "file_name": message_in_creation.file_name,
                "file_link": message_in_creation.file_link,
            }
        )
        return await self.get_message_by_id(message_row.id)

    async def get_message_by_id(self, message_id: int) -> MessageSchema:
        """Get message by id."""
        row = await self._session.execute(
            select(MessageModel).where(MessageModel.id == message_id)
        )
        message = row.scalars().unique().first()
        return MessageSchema.model_validate(message)

    async def get_all(self) -> List[MessageSchema]:
        """Get all objects."""
        messages_in_db = await self._crud.all()
        return [MessageSchema.model_validate(message) for message in messages_in_db]

    async def get_messages_by_attributes(self, attributes: Dict[str, Any]) -> List[MessageSchema]:
        """
        Получение сообщений по заданным атрибутам.

        :param attributes: Словарь атрибутов и их значений для фильтрации. Пример: {"chat_id": 1, "sender_id": 2}
        :return: Список сообщений, соответствующих заданным атрибутам.
        """
        query = select(MessageModel)
        for attribute, value in attributes.items():
            query = query.where(getattr(MessageModel, attribute) == value)

        result = await self._session.execute(query)
        messages = result.scalars().all()
        return [MessageSchema.model_validate(message) for message in messages]
