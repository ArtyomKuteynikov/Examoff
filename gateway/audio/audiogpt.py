import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from sqlalchemy import select
from gateway.db.audio.models import AudioMessage

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))

load_dotenv()


async def generate_answer(chat_id: int, session):
    messages = await session.execute(
        select(AudioMessage).where(AudioMessage.chat_id == chat_id)
    )
    messages = [msg[0].text for msg in messages]
    response = await client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
    )
    return response
