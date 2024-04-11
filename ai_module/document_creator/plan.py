"""Составление плана работы."""
import json

from ai_module.openai_utilities.openai_api_client import create_openai_completion
from ai_module.schemas.enums import GPT_Model
from ai_module.schemas.message import UserMessage, SystemMessage
from gateway.resources import json_data as json_data_templates
from gateway.schemas.enums import DiplomaChatStateEnum
from gateway.config.database import get_db
from gateway.db.messages.repo import MessageRepo
from gateway.resources import strings


async def generate_user_diploma_plan(chat_id: int) -> str:
    """
    Генерирует план дипломной работы по данным, собранным в чате. Возвращает string, в котором содержится план.

    :param chat_id: Id чата.
    :return: План дипломной работы.
    """
    async for session in get_db():
        repo = MessageRepo(session)
        messages = await repo.get_messages_by_attributes({"chat_id": chat_id})

        # Фильтрация сообщений, где остаются только сообщения пользователя и последний ответы на вопрос.
        filtered_messages = [message for message in messages if message.response_specific_state is not None]

        dict_messages = {}
        for message in filtered_messages:
            dict_messages[message.response_specific_state] = message

        plan_request = (
                f"Привет, напиши мне план по дипломной работе с темой "
                f"`{dict_messages[DiplomaChatStateEnum.ASK_THEME]}`.\n"
                f"Где объем работы: {dict_messages[DiplomaChatStateEnum.ASK_WORK_SIZE]}\n"
                f"Требования по работе: {dict_messages[DiplomaChatStateEnum.ASK_OTHER_REQUIREMENTS]}\n"
                f"Источники информации: {dict_messages[DiplomaChatStateEnum.ASK_INFORMATION_SOURCE]}\n"
                f"Дополнительная информация: {dict_messages[DiplomaChatStateEnum.ASK_ANY_INFORMATION]}\n"
                "___\n"
                "Пример плана:\n" +
                strings.PLAN_STRUCTURE_MESSAGE +
                "___\n"
                "Напиши мне только план, без любых вводных конструкций, и не говори мне конечно."
        )

        request_to_nlp = [
            SystemMessage(content=strings.SYSTEM_CONTEXT_HELPER_DIPLOMA_ASK_ACCEPT_PLAN),
            UserMessage(content=plan_request),
        ]
        completion = create_openai_completion(
            model=GPT_Model.GPT_3_5_TURBO_0125,
            messages=request_to_nlp,
            temperature=1.8
        )
        return completion.content


def transform_user_plan_to_dict(plan_text: str, temperature: float = None, request_counter: int = 0):
    """
    Создает JSON плана из str ответа NLP модели.
    Если не получается сгенерировать план 10 раз, то возвращает `None`.

    :param plan_text: Текст плана, сгенерированной от nlp модели.

    :param temperature: Доступные значения от 0 до 2.
        Более высокие значения, например 0,8, сделают выходные данные более случайными, в то время как более низкие
        значения, например 0,2, сделают их более целенаправленными и детерминированными.
    :param request_counter: Количество вызовов функции.

    :return: JSON плана.
    Example:
         {
            "Введение": [],
            "Глава 1. Основные положения ликвидации юридических лиц": [
                "1.1. Основания и способы ликвидации юридических лиц.",
                "1.2. Ликвидация вследствие признания организации (юридического лица) банкротом."
            ],
            "Глава 2. Порядок ликвидации": [
                "2.1. Процедура ликвидации юридического лица.",
                "2.2. Выплаты денежных сумм кредиторам. Завершение ликвидации."
            ],
            "Глава 3. Проблемные вопросы ликвидации юридических лиц": [
                "3.1. Новеллы в ликвидации юридических лиц",
                "3.2. Основные проблемы при ликвидации юридических лиц."
            ],
            "Заключение": [],
            "Список используемой литературы": []
        }
    """
    if request_counter == 10:
        return None

    text = (
            "Привет, у меня есть план работы. Мне нужно, чтобы ты вывел его в json формате."
            "Пример json формата:\n" +
            str(json_data_templates.JSON_PLAN_TEMPLATE) +
            "___"
            "План работы, который мне нужно, чтобы ты вывел в разметке json формате:" +
            str(plan_text)
    )
    request_to_nlp = [
        SystemMessage(content=strings.NOT_YET_MESSAGE2),  # todo Поменять системное сообщение
        UserMessage(content=text),
    ]
    completion = create_openai_completion(
        model=GPT_Model.GPT_4_0613,
        messages=request_to_nlp,
        temperature=temperature,
    )

    # Если не получилось перевести str в json.
    try:
        json_part = completion.content.split('\n{')[1].split('}')[0]
        json_data = '{' + json_part + '}'
        return json.loads(json_data)
    except IndexError:
        transform_user_plan_to_dict(plan_text=plan_text, temperature=2.0, request_counter=request_counter + 1)
