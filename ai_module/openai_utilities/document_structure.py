"""Обработка сообщения пользователя с использованием ai."""
import asyncio
import json
import os

from docx import Document
from dotenv import load_dotenv
from openai import OpenAI

from ai_module.document_creator.document import init_styles, write_chapter
from ai_module.schemas.enums import GPT_Model
from ai_module.schemas.message import UserMessage, SystemMessage, AssistantMessage, messages_to_openai_format
from gateway.resources.strings import PLAN_STRUCTURE_MESSAGE
from gateway.schemas.enums import DiplomaChatStateEnum, ChatTypeTranslate
from gateway.config.database import get_db, async_session_maker
from gateway.db.messages.repo import MessageRepo
from gateway.resources import strings
from test_case_from_prompt_engineer import promts

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))


async def generate_test_structure(type_work, plan, func_count=0):
    if func_count == 10:
        return
    try:
        user_chapter_prompt = promts.CHAPTER_PROMPT.format(
            TYPE=type_work,
            ELEMENT_NAME='Введение',
            ELEMENT_NUM=1,
            CHAR_CAPPACITY=1000,
        )
        messages = [
            {"role": "system", "content": f"{promts.GENERAL_PROMPT}"},
            {"role": "user", "content": f"Plan: ```\n{plan}\n```"},
            {"role": "user", "content": f"{user_chapter_prompt}"}
        ]

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            response_format={"type": "json_object"},
            messages=messages,
        )
        chapter = json.loads(response.choices[0].message.content)
        return chapter['Content']
    except Exception:
        return generate_test_structure(type_work, plan, func_count + 1)


async def generate_text_for_chapter(
        plan,
        element,
        type_work,
        element_name,
        element_num,
        chapter_capacity,
        generation_text='',
):
    """
    Генерация текста для главы.
    """
    user_chapter_prompt = promts.CHAPTER_PROMPT.format(
        TYPE=type_work,
        ELEMENT_NAME=element_name,
        ELEMENT_NUM=element_num,
        CHAR_CAPPACITY=chapter_capacity,
    )
    messages = [
        {"role": "system", "content": f"{promts.GENERAL_PROMPT}"},
        {"role": "user", "content": f"Plan: ```\n{plan}\n```"},
        {"role": "user", "content": f"{user_chapter_prompt}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=messages,
    )
    try:
        next_gen = json.loads(response.choices[0].message.content)
        generation_text += next_gen['Content']
    except Exception:
        return generation_text

    if len(generation_text) < chapter_capacity:
        return await generate_text_for_chapter(
            plan,
            element,
            type_work,
            element_name,
            element_num,
            chapter_capacity,
            generation_text=generation_text,
        )
    return generation_text


async def generate_document(document_name, plan):
    doc = Document()
    init_styles(doc)

    for element in plan:
        print('Start generate_document', document_name, element)
        if element.startswith("Element-"):
            print('Start element', element)
            text = await generate_text_for_chapter(
                plan=plan,
                element=element,
                type_work='Дипломная работа',
                element_name=plan[element]['Name'],
                element_num=element[8:],
                chapter_capacity=plan[element]['Character capacity'],
            )
            write_chapter(doc, plan[element]['Name'], text, 1)

    doc.save(f'files/{document_name}.docx')

