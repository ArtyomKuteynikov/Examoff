"""Message model module."""
from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime

from gateway.db.sqlalchemy_db import Base


class MessageModel(Base):
    """Message model."""

    __tablename__ = "messenger_message"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    chat_id: int = Column(ForeignKey("messenger_chat.id", ondelete="CASCADE"), primary_key=True)
    text: str = Column(String, nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False)
    sender_id: int = Column(ForeignKey("auth_user.id", ondelete="CASCADE"), primary_key=True)
