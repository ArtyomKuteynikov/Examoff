"""Обработчик состояний чата для заказа эссе."""
import uuid

from ai_module.openai_utilities.document_structure import generate_test_structure, generate_document
from ai_module.openai_utilities.message_handler import handle_question_ask_work_size
from ai_module.openai_utilities.plan import generate_plan_via_chat, get_work_plan_from_db
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_message_in_websockets, send_ask_accept_work_plan_buttons
from gateway.config.database import async_session_maker
from gateway.db.files.repo import FileRepo
from gateway.resources import strings
from gateway.resources.chat_state_strings import writing_state_strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import WritingChatStateEnum, ChatTypeTranslate, WebsocketMessageType
from gateway.schemas.file import FileCreateSchema
from gateway.schemas.message import MessageSchema
from gateway.schemas.websocket_data import WebsocketMessageData, websocket_message_data_to_websocket_format


class WritingChatStateHandler:
    """
    Обработчик состояния для заказа эссе.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            WritingChatStateEnum.ASK_THEME: self._writing_ask_theme,
            WritingChatStateEnum.ASK_WORK_SIZE: self._writing_ask_work_size,
            WritingChatStateEnum.ASK_OTHER_REQUIREMENTS: self._writing_ask_other_requirements,
            WritingChatStateEnum.ASK_INFORMATION_SOURCE: self._writing_ask_information_source,
            WritingChatStateEnum.ASK_WRITING_STYLE: self._writing_ask_writing_style,
            WritingChatStateEnum.ASK_ANY_INFORMATION: self._writing_ask_any_information,
            WritingChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE: self._writing_ask_accept_text_structure,
            WritingChatStateEnum.DIALOG_IS_OVER: self._writing_dialog_is_over,
        }

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
            message_text=writing_state_strings.WRITING_WELCOME_MESSAGE,
            state=WritingChatStateEnum.WELCOME_MESSAGE,
        )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_THEME,
            state=WritingChatStateEnum.ASK_THEME,
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

    @staticmethod
    async def _writing_ask_theme(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_WORK_SIZE,
            state=WritingChatStateEnum.ASK_WORK_SIZE,
        )

    @staticmethod
    async def _writing_ask_work_size(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_WORK_SIZE`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        answer = handle_question_ask_work_size(message.text)
        if not answer:
            await repeat_state_message(
                connections=connections,
                chat=chat,
                message_text=writing_state_strings.WRITING_ASK_WORK_SIZE,
            )
        elif answer:
            await create_system_message_in_db(
                chat=chat, text=str(answer), response_specific_state='JSON_WORK_SIZE'
            )
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=writing_state_strings.WRITING_WRITING_ASK_OTHER_REQUIREMENTS,
                state=WritingChatStateEnum.ASK_OTHER_REQUIREMENTS,
            )

    @staticmethod
    async def _writing_ask_other_requirements(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_OTHER_REQUIREMENTS`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_INFORMATION_SOURCE,
            state=WritingChatStateEnum.ASK_INFORMATION_SOURCE,
        )

    @staticmethod
    async def _writing_ask_information_source(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_INFORMATION_SOURCE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_WRITING_STYLE,
            state=WritingChatStateEnum.ASK_WRITING_STYLE,
        )

    @staticmethod
    async def _writing_ask_writing_style(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_WRITING_STYLE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_ANY_INFORMATION,
            state=WritingChatStateEnum.ASK_ANY_INFORMATION,
        )

    @staticmethod
    async def _writing_ask_any_information(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ANY_INFORMATION`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await repeat_state_message(
            connections=connections,
            chat=chat,
            message_text='Идет генерация структуры работы ...',
        )
        plan = await generate_plan_via_chat(chat)
        if not plan:
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text='Произошла ошибка генерации. Создайте заказ заново.',
                state=WritingChatStateEnum.ASK_ANY_INFORMATION,
            )
            return

        await create_system_message_in_db(
            chat=chat, text=str(plan), response_specific_state='JSON_PLAN'
        )

        text_structure = await generate_test_structure(type_work=ChatTypeTranslate[chat.chat_type].value, plan=plan)
        if not text_structure:
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text='Произошла ошибка генерации. Создайте заказ заново.',
                state=WritingChatStateEnum.ASK_ANY_INFORMATION,
            )
            return
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=writing_state_strings.WRITING_ASK_ACCEPT_TEXT_STRUCTURE.format(
                text_structure=text_structure
            ),
            state=WritingChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
        )
        await send_ask_accept_work_plan_buttons(connections, chat)

    async def _writing_ask_accept_text_structure(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_TEXT_STRUCTURE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        plan = eval(await get_work_plan_from_db(chat))
        if message.text not in ["Да, согласен", "Нет, не согласен"]:
            message.text = 'Да, согласен'
            await self._writing_ask_any_information(chat, message, connections)

        elif message.text == 'Да, согласен':
            file_uuid = uuid.uuid4()

            await repeat_state_message(
                connections=connections,
                chat=chat,
                message_text='Идет генерация документа. Не закрывайте окно!',
            )
            await generate_document(file_uuid, plan)

            # Сохранение информации о файле в базу данных
            db_file = FileCreateSchema(
                id=file_uuid,
                user_id=chat.user_owner_id,
                chat_id=chat.id,
            )

            async with async_session_maker() as session:
                repo = FileRepo(session=session)
                await repo.create_file(db_file)

            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=writing_state_strings.WRITING_DIALOG_IS_OVER,
                state=WritingChatStateEnum.DIALOG_IS_OVER,
            )

            await create_system_message_in_db(chat, str(file_uuid), response_specific_state='file')
            websocket_message = WebsocketMessageData(
                sender=WebsocketMessageType.SERVER,
                data={
                    "file": f'{file_uuid}',
                },
            )
            for connect in connections[chat.id]:
                data = websocket_message_data_to_websocket_format(websocket_message)
                await connect.send_text(data)

        elif message.text == 'Нет, не согласен':
            message.text = "Да, согласен"
            await self._writing_ask_accept_text_structure(chat, message, connections)

    @staticmethod
    async def _writing_dialog_is_over(chat: ChatSchema, message, connections) -> None:
        await repeat_state_message(
            connections=connections,
            chat=chat,
            message_text='Работа завершена. Если хотите начать заново, начните новый заказ.',
        )
