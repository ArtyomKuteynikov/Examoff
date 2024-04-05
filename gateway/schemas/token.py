"""
Dataclass JWT_TOKEN.
"""

from pydantic import BaseModel


class JWTTokenPayloadDataSchema(BaseModel):
    """
    JWT Токен для аутентификации пользователя в чате.
    =================================================

    Class properties
    ----------------

    chat_id: int
        Идентификатор чата, для которого откроется соединение.

    user_id: int
        Идентификатор пользователя токена.
    """
    chat_id: int
    user_id: int
