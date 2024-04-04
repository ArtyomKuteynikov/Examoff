"""Message repo."""
from typing import List


from gateway.db.crud import CRUD
from gateway.db.sqlalchemy_db import AsyncSession
from gateway.db.messages.models import MessageModel
from gateway.schemas.message import MessageSchema


class MessageRepo:
    def __init__(self, session: AsyncSession):
        """Initialize repo with CRUD."""
        self._session = session
        self._crud = CRUD(session=session, cls_model=MessageModel)

    async def get_all(self) -> List[MessageSchema]:
        """Get all objects."""
        messages_in_db = await self._crud.all()
        return [record for record in messages_in_db]
