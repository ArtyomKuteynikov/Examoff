import asyncio
import datetime
import json
import os
import uuid
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from gateway.audio.audiogpt import generate_answer
from gateway.config.main import SECRET_AUTH
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, UploadFile
from fastapi import HTTPException
from gateway.config.database import async_session_maker, get_db
import jwt

from fastapi_jwt_auth import AuthJWT
from gateway.db.auth.models import Customer
from gateway.db.audio.models import AudioMessage, AudioChat, AudioChatFile
from sqlalchemy import select
from gateway.audio.processing import processing
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/audio",
    tags=["Audio"]
)

CHATGPT_MOCK = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'''


async def check_token(token: str):
    try:
        data = jwt.decode(str(token), SECRET_AUTH, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    print(data)
    if 'chat_id' in data and 'user_id' in data:
        return data['chat_id'], data['user_id']
    else:
        return None


class ConnectionManager:
    def __init__(self):
        self.connections: dict = defaultdict(dict)
        self.generator = self.get_notification_generator()

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        if self.connections[room_id] == {} or len(self.connections[room_id]) == 0:
            self.connections[room_id] = []
        self.connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: int):
        self.connections[room_id].remove(websocket)

    async def get_notification_generator(self):
        while True:
            message = yield
            msg = message["message"]
            room_name = message["room_name"]
            await self._notify(msg, room_name)

    def get_members(self, room_id: int):
        try:
            return self.connections[room_id]
        except Exception:
            return None

    async def broadcast(self, message: dict, room_id: int, sender: int):
        message_text = message['message']
        msg = await self.add_messages_to_database(message_text, room_id, sender)
        data = {"message": message_text, "message_id": msg.id}
        for connection in self.connections[room_id]:
            try:
                await connection.send_text(json.dumps(data))
            except:
                self.connections[room_id].remove(connection)

    @staticmethod
    async def add_messages_to_database(message: str, room_id: int, sender: int):
        async with async_session_maker() as session:
            msg = AudioMessage(
                chat_id=room_id,
                sender=sender,
                text=message,
                created_at=datetime.datetime.now()
            )
            session.add(msg)
            await session.commit()
        return msg


manager = ConnectionManager()


@router.websocket('/ws')
async def websocket(websocket: WebSocket, token: str = Query(...)):
    room_id, current_user = await check_token(token)
    if not room_id or not current_user:
        raise HTTPException(status_code=418, detail='INCORRECT TOKEN')
    await manager.connect(websocket, room_id)
    try:
        while True:
            _ = await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)


@router.post("/")
async def create_audio_chat(Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    new_chat = AudioChat(owner_id=current_user)
    session.add(new_chat)

    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()

    if not user:
        return HTTPException(status_code=404, detail="USER NOT FOUND")

    if not user[0].audio_file or not os.path.exists(f'{os.getcwd()}/gateway/audio/audio_files/{user[0].audio_file}'):
        raise HTTPException(status_code=418, detail="TEST AUDIO NOT LOADED YET")

    await session.commit()
    await session.refresh(new_chat)
    return new_chat


@router.get("/no-file")
async def do_not_upload_file(chat_id: int, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    chat = await session.execute(
        select(AudioChat).where((AudioChat.id == chat_id) & (AudioChat.owner_id == current_user))
    )
    chat = chat.fetchone()
    if not chat:
        raise HTTPException(status_code=404, detail="CHAT NOT FOUND")

    if chat[0].state not in [0]:
        raise HTTPException(status_code=418, detail="INCORRECT STATE")

    chat[0].state = 2
    await session.commit()
    await session.refresh(chat[0])
    return chat[0]


@router.get("/start")
async def do_not_upload_file(chat_id: int, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    chat = await session.execute(
        select(AudioChat).where((AudioChat.id == chat_id) & (AudioChat.owner_id == current_user))
    )
    chat = chat.fetchone()
    if not chat:
        return HTTPException(status_code=404, detail="CHAT NOT FOUND")

    if chat[0].state not in [1, 2]:
        raise HTTPException(status_code=418, detail="INCORRECT STATE")

    chat[0].state = 3
    await session.commit()
    await session.refresh(chat[0])
    return chat[0]


@router.get("/pause")
async def do_not_upload_file(chat_id: int, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    chat = await session.execute(
        select(AudioChat).where((AudioChat.id == chat_id) & (AudioChat.owner_id == current_user))
    )
    chat = chat.fetchone()
    if not chat:
        return HTTPException(status_code=404, detail="CHAT NOT FOUND")

    if chat[0].state not in [3]:
        raise HTTPException(status_code=418, detail="INCORRECT STATE")

    chat[0].state = 4
    await session.commit()
    await session.refresh(chat[0])
    return chat[0]


@router.get("/finish")
async def do_not_upload_file(chat_id: int, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    chat = await session.execute(
        select(AudioChat).where((AudioChat.id == chat_id) & (AudioChat.owner_id == current_user))
    )
    chat = chat.fetchone()
    if not chat:
        return HTTPException(status_code=404, detail="CHAT NOT FOUND")

    if chat[0].state not in [3, 4]:
        raise HTTPException(status_code=418, detail="INCORRECT STATE")

    chat[0].state = 5
    await session.commit()
    await session.refresh(chat[0])
    return chat[0]


@router.post("/file/upload")
async def upload_file(
        chat_id: int,
        file: UploadFile,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db)
):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    chat = await session.execute(
        select(AudioChat).where((AudioChat.id == chat_id) & (AudioChat.owner_id == current_user))
    )
    chat = chat.fetchone()
    if not chat:
        return HTTPException(status_code=404, detail="CHAT NOT FOUND")

    if chat[0].state not in [0, 2]:
        raise HTTPException(status_code=418, detail="INCORRECT CHAT STATE")

    if not file.filename.endswith(('.docx', '.txt')):
        return HTTPException(status_code=418, detail=f"INCORRECT FILE FORMAT {file.filename}")

    filename = f'{uuid.uuid4()}.{file.filename.split(".")[-1]}'
    contents = await file.read()
    with open(f'{os.getcwd()}/gateway/audio/files/{filename}', 'wb') as f:
        f.write(contents)
    record = AudioChatFile(
        chat_id=chat_id,
        user_id=current_user,
        file=filename
    )
    chat[0].state = 1
    session.add(record)
    await session.commit()
    return {
        "success": True,
        "result": filename
    }


@router.get("/file/download")
async def download_file(
        filename: str,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db)
):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    file = await session.execute(
        select(AudioChatFile).where((AudioChatFile.file == filename) & (AudioChatFile.user_id == current_user))
    )
    if not file:
        return HTTPException(status_code=404, detail="FILE NOT FOUND")
    return FileResponse(path=f'{os.getcwd()}/gateway/audio/files/{filename}', filename=filename,
                        media_type='multipart/form-data')


@router.get("/")
async def get_chats(Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    chats = await session.execute(
        select(AudioChat).where((AudioChat.owner_id == current_user))
    )
    chats = chats.fetchall()
    return [
        chat[0] for chat in chats
    ]


@router.get("/{chat_id:int}")
async def get_chat(chat_id: int, Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    chat = await session.execute(
        select(AudioChat).where((AudioChat.id == chat_id) & (AudioChat.owner_id == current_user))
    )
    chat = chat.fetchone()
    if not chat:
        return HTTPException(status_code=404, detail="CHAT NOT FOUND")
    messages = await session.execute(
        select(AudioMessage).where(AudioMessage.chat_id == chat_id)
    )
    files = await session.execute(
        select(AudioChatFile).where(AudioChatFile.chat_id == chat_id)
    )
    return {
        'chat': chat[0],
        'messages': [message[0] for message in messages],
        'files': [file[0] for file in files],
        'token': jwt.encode({"chat_id": chat_id, "user_id": current_user}, SECRET_AUTH, algorithm="HS256").decode(
            'utf-8')
    }


@router.post("/voice-test/upload")
async def upload_audio_test(
        file: UploadFile,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db)
):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()
    if not user:
        return HTTPException(status_code=404, detail="USER NOT FOUND")

    if user[0].audio_file:
        if os.path.exists(f'{os.getcwd()}/gateway/audio/audio_files/{user[0].audio_file}'):
            os.remove(f'{os.getcwd()}/gateway/audio/audio_files/{user[0].audio_file}')

    filename = f'{uuid.uuid4()}.wav'
    contents = await file.read()
    with open(f'{os.getcwd()}/gateway/audio/audio_files/{filename}', 'wb') as f:
        f.write(contents)
    user[0].audio_file = filename
    await session.commit()
    return {"success": True}


@router.post("/voice/upload")
async def upload_audio(
        chat_id: int,
        file: UploadFile,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db)
):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = await session.execute(
        select(Customer).where((Customer.id == current_user))
    )
    user = user.fetchone()

    if not user:
        return HTTPException(status_code=404, detail="USER NOT FOUND")

    if not user[0].audio_file or not os.path.exists(f'{os.getcwd()}/gateway/audio/audio_files/{user[0].audio_file}'):
        raise HTTPException(status_code=418, detail="TEST AUDIO NOT LOADED YET")

    filename = f'{uuid.uuid4()}.wav'
    contents = await file.read()
    with open(f'{os.getcwd()}/gateway/audio/audio_files/{filename}', 'wb') as f:
        f.write(contents)
    result = asyncio.to_thread(processing, f'{os.getcwd()}/gateway/audio/audio_files/{user[0].audio_file}',
                               f'{os.getcwd()}/gateway/audio/audio_files/{filename}')
    # if os.path.exists(f'{os.getcwd()}/gateway/audio/audio_files/{filename}'):
    #     os.remove(f'{os.getcwd()}/gateway/audio/audio_files/{filename}')
    if result:
        await manager.broadcast({'message': result}, chat_id, sender=0)
        await manager.broadcast({'message': generate_answer(chat_id, session)}, chat_id, sender=1)
        return {
            "author": "professor",
            "result": result
        }
    return {
        "author": "student",
        "result": None
    }
