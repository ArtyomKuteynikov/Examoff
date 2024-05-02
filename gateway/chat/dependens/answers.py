from gateway.config.database import add_messages_to_database, get_db
from gateway.db.chats.repo import ChatRepo
from gateway.resources import strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import WebsocketMessageType
from gateway.schemas.message import MessageInCreationSchema
from gateway.schemas.websocket_data import WebsocketMessageData, websocket_message_data_to_websocket_format


async def create_system_message_in_db(chat: ChatSchema, text: str, response_specific_state=None) -> None:
    """
    Добавление сообщения в БД.

    :param chat: Чат с пользователем.
    :param text: Текст сообщения.
    :param response_specific_state: Статус чата у сообщения.
    """
    message_in_creation = MessageInCreationSchema(
        chat_id=chat.id,
        text=text,
        sender_id=1,  # todo Change to Admin ID
        response_specific_state=response_specific_state,
    )
    await add_messages_to_database(message_in_creation)


async def change_chat_state(chat: ChatSchema, state) -> None:
    """
    Обновления состояния чата в БД.

    :param chat: Чат с пользователем.
    :param state: Новое состояние чата.
    """
    async for session in get_db():
        chat_repo = ChatRepo(session)
        chat.chat_state = state
        await chat_repo.update_chat(chat)


async def send_message_in_websockets(connections, chat: ChatSchema, message_text: str) -> None:
    """
    Отправляет сообщение по websockets.

    :param connections: Список соединений по websocket.
    :param chat: Чат с пользователем.
    :param message_text: Текст сообщения для отправки.
    """
    websocket_message = WebsocketMessageData(
        message_type=WebsocketMessageType.SYSTEM_MESSAGE,
        data={
            "message_text": message_text,
        },
    )
    # Отправка только по каналам, что относятся к чату.
    try:
        for connect in connections[chat.id]:
            data = websocket_message_data_to_websocket_format(websocket_message)
            await connect.send_text(data)
    except Exception as e:
        print(e)


async def send_message_and_change_state(connections, chat: ChatSchema, message_text: str, state) -> None:
    """
    Отправляет сообщение по websockets, сохраняет в бд и меняет состояние чата.

    :param connections: Список соединений по websocket.
    :param chat: Чат с пользователем.
    :param message_text: Текст сообщения для отправки.
    :param state: Новое состояние чата.
    """
    await create_system_message_in_db(chat, message_text)
    await change_chat_state(chat, state)
    await send_message_in_websockets(connections, chat, message_text)


async def repeat_state_message(connections, chat: ChatSchema, message_text: str) -> None:
    """
    Отправляет сообщение по websockets и сохраняет в бд.
    Случай использования:
        Пользователь неправильно или неточно ответил на вопрос.
        Система отправляет пользователь вопрос заново.

    :param connections: Список соединений по websocket.
    :param chat: Чат с пользователем.
    :param message_text: Текст сообщения для отправки.
    """
    await create_system_message_in_db(chat, message_text)
    await send_message_in_websockets(connections, chat, message_text)


async def send_ask_accept_work_plan_buttons(connections, chat: ChatSchema):
    yes_button = {
        "message_type": "system_message",
        "data": {
            "button": "Да, согласен"
        }
    }
    no_button = {
        "message_type": "system_message",
        "data": {
            "button": "Нет, не согласен"
        }
    }
    await send_message_in_websockets(connections, chat, str(yes_button))
    await send_message_in_websockets(connections, chat, str(no_button))
