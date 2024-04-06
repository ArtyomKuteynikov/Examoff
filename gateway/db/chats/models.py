"""Chat model module."""
from sqlalchemy import Column, String, Integer
from gateway.db.sqlalchemy_db import Base


class ChatModel(Base):
    """Chat model."""
    __tablename__ = "messenger_chat"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    chat_state: str = Column(String(100), nullable=True)
    chat_type: str = Column(String(50), nullable=False, default="DIPLOMA_CHAT_TYPE")
