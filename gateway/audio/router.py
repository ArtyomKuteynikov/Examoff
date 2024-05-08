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


async def validate_token(token: str):
    try:
        data = jwt.decode(str(token), SECRET_AUTH, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidSignatureError:
        return None

    async for session in get_db():
        chat_repo = ChatRepo(session)
        chat = await chat_repo.get_chat_by_id(data['chat_id'])

        if data['user_id'] == chat.user_owner_id:
            return JWTTokenPayloadDataSchema(
                user_id=data['user_id'],
                chat_id=data['chat_id']
            )


class ConnectionManager:
    def __init__(self):
        self.connections: dict = defaultdict(dict)
        self.generator = self.get_notification_generator()
        self.fsm = FSM()

    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()
        if self.connections[chat_id] == {} or len(self.connections[chat_id]) == 0:
            self.connections[chat_id] = []
        self.connections[chat_id].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: int):
        self.connections[chat_id].remove(websocket)

    async def check_first_connection(self, chat: ChatSchema):
        if chat.chat_state is None:
            await self.fsm.init_first_message(chat, self.connections)

    async def get_notification_generator(self):
        while True:
            message = yield
            msg = message["message"]
            room_name = message["room_name"]
            await self._notify(msg, room_name)

    def get_members(self, chat_id: int):
        try:
            return self.connections[chat_id]
        except Exception:
            return None

    async def broadcast(
            self,
            websocket: WebSocket,
            websocket_message: WebsocketMessageData,
            chat: ChatSchema,
            user_id: int
    ):
        if websocket_message.message_type == WebsocketMessageType.USER_MESSAGE:
            message_in_creation = MessageInCreationSchema(
                chat_id=chat.id,
                text=websocket_message.data["message_text"],
                sender_id=user_id,
                response_specific_state=chat.chat_state,
            )
            message_ib_db = await add_messages_to_database(message_in_creation)
            if len(self.connections[chat.id]):
                await self.repeat_user_message_to_other_connections(websocket, chat.id, websocket_message)

            await self.fsm.fsm_handle_message(chat, message_ib_db, self.connections)

    async def send_websocket_message(self, chat_id: int):
        for connect in self.connections[chat_id]:
            await connect.send_text(f"Hello")

    async def repeat_user_message_to_other_connections(
            self,
            websocket: WebSocket,
            chat_id: int,
            message: WebsocketMessageData,
    ):
        return
        # todo пофиксить баг
        message_to_send = message
        for connect in self.connections[chat_id]:
            if connect == websocket:
                continue
            message_to_send.message_type = WebsocketMessageType.USER_MESSAGE_FROM_OTHER_SOCKET
            data = websocket_message_data_to_websocket_format(message_to_send)
            await connect.send_text(data)


manager = ConnectionManager()


@router.websocket('/ws/')
async def websocket_connection(websocket: WebSocket, token: str = Query(...), session: AsyncSession = Depends(get_db)):
    connection_data = await validate_token(token)
    if not connection_data:
        raise WebSocketException(code=403, reason='incorrect_token')
    await manager.connect(websocket, connection_data.chat_id)

    chat_repo = ChatRepo(session=session)
    chat = await chat_repo.get_chat_by_id(connection_data.chat_id)
    await manager.check_first_connection(chat)
    try:
        while True:
            json_data = await websocket.receive_json()
            websocket_message_data = WebsocketMessageData(
                message_type=json_data['message_type'],
                data=json_data['data'],
            )
            await manager.broadcast(websocket, websocket_message_data, chat, connection_data.user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, connection_data.chat_id)


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
        return {"Status": f"OK"}
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
            return {
                "author": "professor",
                "result": result
            }
        return {
            "author": "student",
            "result": None
        }
    return HTTPException(status_code=403, detail="Auth failed.")
