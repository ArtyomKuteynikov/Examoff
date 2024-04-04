import json
from collections import defaultdict
from gateway.config.main import SECRET_AUTH
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi import HTTPException
from gateway.config.database import async_session_maker
import jwt

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


async def check_token(token: str):
    try:
        data = jwt.decode(str(token), SECRET_AUTH, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    if 'user_id' in data and 'room_id' in data:
        return data['user_id'], data['room_id']
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

    async def broadcast(self, message: dict, room_id: int, user_id):
        message_text = message['message']
        msg = await self.add_messages_to_database(message_text, room_id, user_id)
        # TODO: начать выполнять обработку через ChatGPT, первым вернуть сообщение
        data = {"message": message_text, "sender": user_id, "message_id": msg}
        for connection in self.connections[room_id]:
            try:
                await connection.send_text(json.dumps(data))
                # TODO: потом вернуть юзеру ответ нейросетки
            except:
                self.connections[room_id].remove(connection)

    @staticmethod
    async def add_messages_to_database(message: str, room_id: int, user_id):
        async with async_session_maker() as session:
            # TODO: добавить сохранение в БД
            # msg = ()
            # session.add(msg)
            # await session.commit()
            pass
        return 'tut'


manager = ConnectionManager()


@router.websocket('/ws/{room_id}')
async def websocket(websocket: WebSocket, token: str = Query(...)):
    data = await check_token(token)
    if not data:
        raise HTTPException(status_code=403, detail='incorrect_token')
    current_user, room_id = data
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data, room_id, current_user)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
