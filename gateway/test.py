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
    encoded_jwt = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjaGF0X2lkIjo5LCJ1c2VyX2lkIjozfQ.w2odW8ruo-vRouEP0OmA3lU9U3fvUQJ8OgC8rZsoNdg'  # jwt.encode({"chat_id": 4, "user_id": 3}, SECRET_AUTH, algorithm="HS256").decode('utf-8')
    uri = f"ws://62.3.12.8:5001/audio/ws?token={encoded_jwt}"

    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            print(f"Received from: {response}")

asyncio.get_event_loop().run_until_complete(connect_to_websocket_server(4))
