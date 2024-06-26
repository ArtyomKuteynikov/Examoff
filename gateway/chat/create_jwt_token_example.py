import os
from dotenv import load_dotenv
import jwt

load_dotenv()

SECRET_AUTH = os.environ.get("SECRET_AUTH")

encoded_jwt = jwt.encode({"chat_id": 25, "user_id": 1}, SECRET_AUTH, algorithm="HS256").decode('utf-8')


print(encoded_jwt)
