import json
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from gateway.chat.chat_states.fsm import FSM
from gateway.config.main import SECRET_AUTH
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi import HTTPException
from gateway.config.database import async_session_maker, get_db
import jwt

from gateway.db.chats.repo import ChatRepo
from gateway.db.messages.repo import MessageRepo
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import WebsocketMessageType
from gateway.schemas.message import MessageSchema, MessageInCreationSchema
from gateway.schemas.token import JWTTokenPayloadDataSchema
from gateway.schemas.websocket_data import WebsocketMessageData, websocket_message_data_to_websocket_format

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


async def validate_token(token: str):
    try:
        data = jwt.decode(str(token), SECRET_AUTH, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    if 'user_id' in data and 'chat_id' in data:
        return JWTTokenPayloadDataSchema(
            user_id=data['user_id'],
            chat_id=data['chat_id']
        )


class ConnectionManager:
    def __init__(self):
        self.connections: dict = defaultdict(dict)
        self.generator = self.get_notification_generator()

    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()
        if self.connections[chat_id] == {} or len(self.connections[chat_id]) == 0:
            self.connections[chat_id] = []
        self.connections[chat_id].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: int):
        self.connections[chat_id].remove(websocket)

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
            )
            msg = await self.add_messages_to_database(message_in_creation)
            if len(self.connections[chat.id]):
                await self.repeat_user_message_to_other_connections(websocket, chat.id, websocket_message)

            fsm = FSM()
            fsm.fsm_handle_message(chat.chat_type, chat.chat_state)

    async def send_websocket_message(self, chat_id: int):
        for connect in self.connections[chat_id]:
            await connect.send_text(f"Hello")

    async def repeat_user_message_to_other_connections(
            self,
            websocket: WebSocket,
            chat_id: int,
            message: WebsocketMessageData,
    ):
        message_to_send = message
        for connect in self.connections[chat_id]:
            if connect == websocket:
                continue
            message_to_send.message_type = WebsocketMessageType.USER_MESSAGE_FROM_OTHER_SOCKET
            data = websocket_message_data_to_websocket_format(message_to_send)
            await connect.send_text(data)

    @staticmethod
    async def add_messages_to_database(message: MessageInCreationSchema) -> MessageSchema:
        async with async_session_maker() as session:
            repo = MessageRepo(session=session)
            return await repo.create_message(message)


manager = ConnectionManager()


@router.websocket('/ws/')
async def websocket_connection(websocket: WebSocket, token: str = Query(...), session: AsyncSession = Depends(get_db)):
    connection_data = await validate_token(token)
    if not connection_data:
        raise HTTPException(status_code=403, detail='incorrect_token')
    await manager.connect(websocket, connection_data.chat_id)
    chat_repo = ChatRepo(session=session)
    chat = await chat_repo.get_chat_by_id(connection_data.chat_id)
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
