"""Обработчик состояний чата для заказа контрольной работы."""
import uuid

from ai_module.openai_utilities.document_structure import generate_test_structure, generate_document
from ai_module.openai_utilities.message_handler import handle_question_ask_work_size
from ai_module.openai_utilities.plan import generate_plan_via_chat, get_work_plan_from_db
from gateway.chat.dependens.answers import send_message_and_change_state, repeat_state_message, \
    create_system_message_in_db, send_ask_accept_work_plan_buttons
from gateway.config.database import async_session_maker
from gateway.db.files.repo import FileRepo
from gateway.resources.chat_state_strings import course_work_state_strings
from gateway.schemas.chat import ChatSchema
from gateway.schemas.enums import CourseWorkChatStateEnum, ChatTypeTranslate, WebsocketMessageType
from gateway.schemas.file import FileCreateSchema
from gateway.schemas.message import MessageSchema
from gateway.schemas.websocket_data import WebsocketMessageData, websocket_message_data_to_websocket_format


class CourseWorkChatStateHandler:
    """
    Обработчик состояния для заказа контрольной работы.
    Содержит в себе методы, что обрабатывают сообщение пользователя.
    """

    def __init__(self):
        """
        Для каждого состояние чата свой сценарий взаимодействия.
        """
        self.state_methods = {
            CourseWorkChatStateEnum.ASK_THEME: self._course_work_ask_theme,
            CourseWorkChatStateEnum.ASK_WORK_SIZE: self._course_work_ask_work_size,
            CourseWorkChatStateEnum.ASK_OTHER_REQUIREMENTS: self._course_work_ask_other_requirements,
            CourseWorkChatStateEnum.ASK_INFORMATION_SOURCE: self._course_work_ask_information_source,
            CourseWorkChatStateEnum.ASK_ANY_INFORMATION: self._course_work_ask_any_information,
            CourseWorkChatStateEnum.ASK_ACCEPT_PLAN: self._course_work_ask_accept_plan,
            CourseWorkChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE: self._course_work_ask_accept_text_structure,
            CourseWorkChatStateEnum.DIALOG_IS_OVER: self._course_work_dialog_is_over,
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
            message_text=course_work_state_strings.COURSE_WORK_WELCOME_MESSAGE,
            state=CourseWorkChatStateEnum.WELCOME_MESSAGE,
        )
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_THEME,
            state=CourseWorkChatStateEnum.ASK_THEME,
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
    async def _course_work_ask_theme(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_THEME`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_WORK_SIZE,
            state=CourseWorkChatStateEnum.ASK_WORK_SIZE,
        )

    @staticmethod
    async def _course_work_ask_work_size(chat: ChatSchema, message, connections) -> None:
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
                message_text=course_work_state_strings.COURSE_WORK_ASK_WORK_SIZE,
            )
        elif answer:
            await create_system_message_in_db(
                chat=chat, text=str(answer), response_specific_state='JSON_WORK_SIZE'
            )
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=course_work_state_strings.COURSE_WORK_ASK_OTHER_REQUIREMENTS,
                state=CourseWorkChatStateEnum.ASK_OTHER_REQUIREMENTS,
            )

    @staticmethod
    async def _course_work_ask_other_requirements(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_OTHER_REQUIREMENTS`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_INFORMATION_SOURCE,
            state=CourseWorkChatStateEnum.ASK_INFORMATION_SOURCE,
        )

    @staticmethod
    async def _course_work_ask_information_source(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_INFORMATION_SOURCE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_ANY_INFORMATION,
            state=CourseWorkChatStateEnum.ASK_ANY_INFORMATION,
        )

    @staticmethod
    async def _course_work_ask_any_information(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ANY_INFORMATION`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """

        await repeat_state_message(
            connections=connections,
            chat=chat,
            message_text='Идет генерация плана...',
        )

        plan = await generate_plan_via_chat(chat)
        if not plan:
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text='Произошла ошибка генерации. Создайте заказ заново.',
                state=CourseWorkChatStateEnum.ASK_ANY_INFORMATION,
            )
            return

        await create_system_message_in_db(
            chat=chat, text=str(plan), response_specific_state='JSON_PLAN'
        )

        plan_structure = ''
        for element in plan:
            if element.startswith("Element-"):
                plan_structure += plan[element]['Name'] + '\n'

        await send_message_and_change_state(
            connections=connections,
            chat=chat,
            message_text=course_work_state_strings.COURSE_WORK_ASK_ACCEPT_PLAN.format(
                course_work_plan=plan_structure
            ),
            state=CourseWorkChatStateEnum.ASK_ACCEPT_PLAN,
        )
        await send_ask_accept_work_plan_buttons(connections, chat)

    async def _course_work_ask_accept_plan(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_PLAN`. Используется ai, чтобы определить цель ответа.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        if message.text not in ["Да, согласен", "Нет, не согласен"]:
            plan = eval(await get_work_plan_from_db(chat))
            plan_structure = ''
            for element in plan:
                if element.startswith("Element-"):
                    plan_structure += plan[element]['Name'] + '\n'

            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=course_work_state_strings.COURSE_WORK_ASK_ACCEPT_PLAN.format(
                    course_work_plan=plan_structure
                ),
                state=CourseWorkChatStateEnum.ASK_ACCEPT_PLAN,
            )
            await send_ask_accept_work_plan_buttons(connections, chat)

        elif message.text == 'Да, согласен':
            await repeat_state_message(
                connections=connections,
                chat=chat,
                message_text='Идет генерация структуры работы ...',
            )
            plan = await get_work_plan_from_db(chat)
            text_structure = await generate_test_structure(type_work=ChatTypeTranslate[chat.chat_type].value, plan=plan)
            if not text_structure:
                await send_message_and_change_state(
                    connections=connections,
                    chat=chat,
                    message_text='Произошла ошибка генерации. Создайте заказ заново.',
                    state=CourseWorkChatStateEnum.ASK_ACCEPT_PLAN,
                )
                return
            await send_message_and_change_state(
                connections=connections,
                chat=chat,
                message_text=course_work_state_strings.COURSE_WORK_ASK_ACCEPT_TEXT_STRUCTURE.format(
                    course_work_text_structure=text_structure
                ),
                state=CourseWorkChatStateEnum.ASK_ACCEPT_TEXT_STRUCTURE,
            )
            await send_ask_accept_work_plan_buttons(connections, chat)

        elif message.text == 'Нет, не согласен':
            message.text = 'Да, согласен'
            await self._course_work_ask_any_information(chat, message, connections)

    async def _course_work_ask_accept_text_structure(self, chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `ASK_ACCEPT_TEXT_STRUCTURE`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        plan = eval(await get_work_plan_from_db(chat))
        if message.text not in ["Да, согласен", "Нет, не согласен"]:
            message.text = 'Да, согласен'
            await self._course_work_ask_accept_plan(chat, message, connections)

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
                message_text=course_work_state_strings.COURSE_WORK_DIALOG_IS_OVER,
                state=CourseWorkChatStateEnum.DIALOG_IS_OVER,
            )

            await create_system_message_in_db(chat, str(file_uuid), response_specific_state='file')
            websocket_message = WebsocketMessageData(
                message_type=WebsocketMessageType.SYSTEM_MESSAGE,
                data={
                    "file": f'{file_uuid}',
                },
            )
            for connect in connections[chat.id]:
                data = websocket_message_data_to_websocket_format(websocket_message)
                await connect.send_text(data)

        elif message.text == 'Нет, не согласен':
            message.text = "Да, согласен"
            await self._course_work_ask_accept_plan(chat, message, connections)

    @staticmethod
    async def _course_work_dialog_is_over(chat: ChatSchema, message, connections) -> None:
        """
        Обработчик для состояния чата `DIALOG_IS_OVER`.

        :param chat: Чат пользователя.
        :param message: Сообщение, отправленное пользователем.
        :param connections: Список подключений по websocket.
        """
        await repeat_state_message(
            connections=connections,
            chat=chat,
            message_text='Работа завершена. Если хотите начать заново, начните новый заказ.',
        )
