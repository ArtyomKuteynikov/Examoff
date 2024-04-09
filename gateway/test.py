import asyncio

import jwt
import websockets

from config.main import SECRET_AUTH


def check_token(token: str):
    try:
        data = jwt.decode(token, SECRET_AUTH, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    if 'role_id' in data and 'room_id' in data:
        return data['role_id'], data['room_id'], (data['staff_id'] if data['role_id'] == 1 else None)
    else:
        return None


async def connect_to_websocket_server(room_id):
    encoded_jwt = jwt.encode({"room_id": room_id, "role_id": 0, "user_id":5},
                             SECRET_AUTH,
                             algorithm="HS256").decode('utf-8')
    uri = f"ws://127.0.0.1:8000/chat/ws/{room_id}?token={encoded_jwt}"  # Replace this with the WebSocket server URI

    async with websockets.connect(uri) as websocket:
        # Receive a message from the server
        while True:
            await websocket.send('{"message": "' + input('---> ') + '"}')
            response = await websocket.recv()
            print(f"Received from {response}: {response}")

asyncio.get_event_loop().run_until_complete(connect_to_websocket_server(28))
