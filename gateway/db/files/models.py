"""Chat model module."""
from sqlalchemy import Column, String, Integer, ForeignKey
from gateway.db.sqlalchemy_db import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class File(Base):
    __tablename__ = 'files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Уникальный идентификатор и название файла
    user_id = Column(Integer)  # ID пользователя, который может скачать файл
    chat_id: int = Column(ForeignKey("messenger_chat.id", ondelete="CASCADE"), primary_key=True)
