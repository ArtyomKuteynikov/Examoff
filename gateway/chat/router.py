import json
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from gateway.chat.chat_states.fsm import FSM
from gateway.config.main import SECRET_AUTH
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi import HTTPException
from gateway.config.database import async_session_maker, get_db, add_messages_to_database
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
        raise HTTPException(status_code=403, detail='incorrect_token')
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


@router.get("/ws/{connect_via_token}", responses={101: {"description": "Switched protocols", }, }, )
async def connect_to_websocket_via_token(
        token: str = Query(...),
):
    """
    Подключение к чату по websocket.

    Для того чтобы подключиться, следует выполнить следующий запрос: <br>
    ws://**{URL_API}**/chat/ws/?token=**{access_token}**.<br><br>

    При успешном подключение отобразиться статус 101 (Switched protocols).
    """


responses_messages_in_websocket = {
    1: {
        "description": "Сообщение отправленное от пользователя по websocket.",
        "content": {
            "application/json": {
                "example": {
                    "message_type": "user_message",
                    "data": {
                        "message_text": "Hello, my name is User."
                    }
                }
            }
        },
    },
    2: {
        "description": "Сообщение отправленное от пользователя по websocket через другое соединение.\n"
                       "Используется для того, чтобы отобразить сообщение от пользователя на всех устройствах, что были"
                       " подключены через websocket.",
        "content": {
            "application/json": {
                "example": {
                    "message_type": "user_message_from_other_socket",
                    "data": {
                        "message_text": "Hello, my name is User."
                    }
                }
            }
        },
    },
    3: {
        "description": "Сообщение отправленное от backend по websocket.",
        "content": {
            "application/json": {
                "example": {
                    "message_type": "system_message",
                    "data": {
                        "message_text": "Response from server."
                    }
                }
            }
        },
    },
}


@router.get("/ws/{messages}", responses=responses_messages_in_websocket)
async def messages_in_websocket(
        message: WebsocketMessageData,
):
    """
    Отправка и получения сообщений по websocket.

    Из-за того, что websocket считается низкоуровневым подключением, спецификации по OpenAPI у него нет. Придется
    костылить документацию.

    Следующие Response соответствуют типам сообщений, передаваемых по websocket.

    1. USER_MESSAGE. Сообщение отправленное от пользователя по websocket.
    1. USER_MESSAGE_FROM_OTHER_SOCKET. Сообщение отправленное от пользователя по websocket через другое соединение.
    2. SYSTEM_MESSAGE. Сообщение отправленное от сервера по websocket.
    """
