from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from gateway.config.main import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASS
from gateway.db.messages.repo import MessageRepo
from gateway.schemas.message import MessageInCreationSchema, MessageSchema

# SQLALCHEMY_DATABASE_URL = config("DATABASE_URL")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
Base = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def add_messages_to_database(message: MessageInCreationSchema) -> MessageSchema:
    async with async_session_maker() as session:
        repo = MessageRepo(session=session)
        return await repo.create_message(message)
