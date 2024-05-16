"""Обработчик состояний чата при работе с файлом."""
from openai.types.beta import VectorStore

from ai_module.openai_utilities.file import create_openai_assistant, upload_vector_store, create_open_ai_thread, client, \
    EventHandler
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_message_in_websockets, change_chat_state
from gateway.chat.processing_message.diploma import process_user_message_on_welcome_message_status, \
    process_user_message_on_ask_work_size_status, generate_user_plan, process_user_message_on_ask_accept_plan_status
from gateway.config.database import async_session_maker
from gateway.db.messages.repo import MessageRepo
from gateway.resources import strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import WorkWithFileChatStateEnum
from gateway.schemas.message import MessageSchema


class WorkWithFileChatStateHandler:
    """
    Обработчик состояния при работе с файлом.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            WorkWithFileChatStateEnum.FILE_ANALYZED: self._work_with_file_file_analyzed,
            WorkWithFileChatStateEnum.START_ASKING: self._work_with_file_start_asking,
        }
        self.assistant = create_openai_assistant()
        self.file: VectorStore

    @staticmethod
    async def _first_message_init(chat: ChatSchema, connections) -> None:
        """
        Обработчик первого подключения по websocket.
        Действие выполняется, когда только создается чат с пользователем и инициализируется
        первое подключение по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.WORK_WITH_FILE_WELCOME_MESSAGE,
            state=WorkWithFileChatStateEnum.FILE_ANALYZED,
        )

    async def handle_message(self, chat: ChatSchema, message: MessageSchema, connections) -> None:
        """
        Определяет какое состояние чата и вызывает соответствующий метод.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        method = self.state_methods.get(chat.chat_state)
        if method:
            await method(chat, message, connections)

    async def _work_with_file_file_analyzed(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `FILE_ANALYZED`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        file_link = message.text
        self.file = upload_vector_store([file_link])
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=strings.WORK_WITH_FILE_START_ASKING,
            state=WorkWithFileChatStateEnum.START_ASKING,
        )

    async def _work_with_file_start_asking(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        async with async_session_maker() as session:
            message_repo = MessageRepo(session)
            messages = await message_repo.get_messages_by_attributes({'chat_id': chat.id,
                                                                      'response_specific_state': 'file_analyzed'})

            filtered_messages = [message for message in messages if message.response_specific_state is not None]
            messages = {}
            for message in filtered_messages:
                messages[message.response_specific_state] = message

            file_path = messages['file_analyzed'].text
        self.file = upload_vector_store([file_path])

        messages = []
        async with async_session_maker() as session:
            message_repo = MessageRepo(session)
            bd_messages = await message_repo.get_messages_by_attributes({'chat_id': chat.id})

            for mes in bd_messages[-9:]:
                if mes.sender_id == 1:
                    messages.append(
                        {"role": "assistant", "content": mes.text}
                    )
                else:
                    messages.append(
                        {"role": "user", "content": mes.text}
                    )
        thread = create_open_ai_thread(self.assistant, self.file, messages=messages)
        print('tut1')
        with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=self.assistant.id,
                instructions="Please address the user as Student. The user has a premium account.",
                event_handler=EventHandler(chat=chat, connections=connections),
        ) as stream:
            print('tut2')
            stream.until_done()
            print('tut3')

        await change_chat_state(chat, WorkWithFileChatStateEnum.START_ASKING)
