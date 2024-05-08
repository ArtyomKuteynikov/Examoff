import json
import os
import uuid
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from gateway.chat.chat_states.fsm import FSM
from gateway.config.main import SECRET_AUTH
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, UploadFile
from fastapi import HTTPException, WebSocketException
from gateway.config.database import async_session_maker, get_db, add_messages_to_database
import jwt

from gateway.db.chats.repo import ChatRepo
from gateway.db.messages.repo import MessageRepo
from gateway.schemas.chat import ChatSchema, ChatInCreationSchema
from gateway.schemas.enums import WebsocketMessageType, ChatType
from gateway.schemas.message import MessageSchema, MessageInCreationSchema
from gateway.schemas.token import JWTTokenPayloadDataSchema
from gateway.schemas.websocket_data import WebsocketMessageData, websocket_message_data_to_websocket_format

from fastapi_jwt_auth import AuthJWT
from gateway.db.auth.models import Customer, Subscriptions
from sqlalchemy import select
from gateway.audio.processing import processing

router = APIRouter(
    prefix="/audio",
    tags=["Audio"]
)


async def check_token(token: str):
    try:
        data = jwt.decode(str(token), SECRET_AUTH, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    if 'role_id' in data and 'room_id' in data:
        return data['role_id'], data['room_id'], (data['staff_id'] if data['role_id'] == 1 else None)
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

    async def broadcast(self, message: dict, room_id: int, role: int, staff_id: int | None = None):
        message_text = message['message']
        msg = await self.add_messages_to_database(message_text, room_id, role, staff_id)
        data = {"message": message_text, "sender": role, "message_id": msg.id}
        print(self.connections)
        for connection in self.connections[room_id]:
            try:
                await connection.send_text(json.dumps(data))
            except:
                self.connections[room_id].remove(connection)

    @staticmethod
    async def add_messages_to_database(message: str, room_id: int, role: int, staff_id: int | None = None):
        async with async_session_maker() as session:
            # msg = OrderMessages(
            #     message=message,
            #     order_id=room_id,
            #     author=role,
            #     manager_id=staff_id,
            #     created=datetime.datetime.now()
            # )
            # session.add(msg)
            await session.commit()
        return  # msg


manager = ConnectionManager()


@router.websocket('/ws/{room_id}')
async def websocket(websocket: WebSocket, token: str = Query(...)):
    data = await check_token(token)
    if not data:
        raise HTTPException(status_code=403, detail='incorrect_token')
    role, room_id, current_user = data
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            if current_user:
                await manager.broadcast(data, room_id, role, staff_id=current_user)
            else:
                await manager.broadcast(data, room_id, role)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)


# TODO: cделать эндпоинт для загрузки файла и эндпоинт для получения
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

    if user and file.filename.endswith('.wav'):
        filename = f'{uuid.uuid4()}.wav'
        contents = await file.read()
        with open(f'{os.getcwd()}/gateway/audio/audio_files/{filename}', 'wb') as f:
            f.write(contents)
        user[0].audio_file = filename
        await session.commit()
        return {"success": True}
    return HTTPException(status_code=403, detail="Auth failed.")


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

    if user and file.filename.endswith('.wav'):
        filename = f'{uuid.uuid4()}.wav'
        contents = await file.read()
        with open(f'{os.getcwd()}/gateway/audio/audio_files/{filename}', 'wb') as f:
            f.write(contents)
        result = processing(f'{os.getcwd()}/gateway/audio/audio_files/{user[0].audio_file}',
                            f'{os.getcwd()}/gateway/audio/audio_files/{filename}')
        if os.path.exists(f'{os.getcwd()}/gateway/audio/audio_files/{filename}'):
            os.remove(f'{os.getcwd()}/gateway/audio/audio_files/{filename}')
        if result:
            # TODO: broadcast message to ws
            # TODO: ask ChatGPT and broadcast response
            return {
                "author": "professor",
                "result": result
            }
        return {
            "author": "student",
            "result": None
        }
    return HTTPException(status_code=403, detail="Auth failed.")
