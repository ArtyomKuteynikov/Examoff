import datetime
from sqlalchemy import DateTime
from sqlalchemy import Column, Integer, String, ForeignKey

from gateway.config.database import Base


class AudioChat(Base):
    __tablename__ = 'audio_chat'

    STATES = [
        (0, 'INIT'),
        (1, 'FILE_LOADED'),
        (2, 'WITHOUT_FILE'),
        (3, 'STARTED'),
        (4, 'PAUSED'),
        (5, 'FINISHED'),
    ]
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('system_customer.id'))
    state = Column(Integer, default=0)


class AudioMessage(Base):
    __tablename__ = 'audio_message'

    SENDERS = [
        (0, 'Преподаватель'),
        (1, 'ChatGPT')
    ]
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('audio_chat.id'))
    sender = Column(Integer)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AudioChatFile(Base):
    __tablename__ = 'audio_chat_files'

    id = Column(Integer, primary_key=True)
    file = Column(String(256))
    user_id = Column(Integer, ForeignKey('system_customer.id'))
    chat_id = Column(Integer, ForeignKey('audio_chat.id'))
