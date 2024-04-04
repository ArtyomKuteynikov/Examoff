"""
Dataclass Message.
"""
from datetime import datetime
from pydantic import BaseModel


class MessageSchema(BaseModel):
    """
    #Todo Написать документацию
    """
    class Config:
        orm_mode = True

    id: int
    chat_id: int
    text: str
    sender_id: int
    created_at: datetime

