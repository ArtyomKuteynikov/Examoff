"""Chat repo."""
import uuid
from typing import List, Dict, Any

from sqlalchemy import select

from gateway.db.crud import CRUD
from gateway.db.sqlalchemy_db import AsyncSession
from gateway.db.files.models import File
from gateway.schemas.file import FileSchema, FileCreateSchema


class FileRepo:
    def __init__(self, session: AsyncSession):
        """Initialize repo with CRUD."""
        self._session = session
        self._crud = CRUD(session=session, cls_model=File)

    async def create_file(self, file_in_creation: FileCreateSchema) -> FileSchema:
        """Create a new File entry."""
        file_row = await self._crud.create(
            model_data={
                "id": file_in_creation.id,
                "user_id": file_in_creation.user_id,
                "chat_id": file_in_creation.chat_id,
            }
        )
        return await self.get_file_by_id(file_row.id)

    async def get_file_by_id(self, file_id: uuid.UUID) -> FileSchema:
        """Get file by UUID."""
        result = await self._session.execute(
            select(File).where(File.id == file_id)
        )
        file = result.scalars().unique().first()
        return FileSchema(
            id=file.id,
            user_id=file.user_id,
            chat_id=file.chat_id,
        )

    async def get_files_by_user_id(self, user_id: int) -> List[FileSchema]:
        """Retrieve files by user_id."""
        result = await self._session.execute(
            select(File).where(File.user_id == user_id)
        )
        files = result.scalars().all()
        return [FileSchema.model_validate(file) for file in files]

    async def get_file_by_chat_id(self, chat_id: int) -> FileSchema:
        """Retrieve files by user_id."""
        result = await self._session.execute(
            select(File).where(File.chat_id == chat_id)
        )
        file = result.scalars().unique().first()
        if not file:
            return None
        return FileSchema(
            id=file.id,
            user_id=file.user_id,
            chat_id=file.chat_id,
        )

    async def delete_file(self, file_id: uuid.UUID) -> None:
        """Delete a file."""
        await self._crud.delete(pkey_val=file_id)
