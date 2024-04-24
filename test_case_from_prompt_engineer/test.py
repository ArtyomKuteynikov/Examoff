import json
import unittest
from dotenv import load_dotenv
import os

from openai import OpenAI

from test_case_from_prompt_engineer import promts
from docx import Document

from test_case_from_prompt_engineer.document import init_styles, write_chapter

load_dotenv()


class OpenAIUtilities(unittest.TestCase):
    def __init__(self, method_name='runTest'):
        super().__init__(method_name)
        self.user_requirements = self.init_user_requirements()
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))
        self.example_plan = self.init_example_plan()

    @staticmethod
    def init_example_plan():
        """
        Возвращает пример плана для работы из файла example_plan.json.
        """
        with open('example_plan.json', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def init_user_requirements():
        """
        Данные о работе, которые ввел пользователь.
        """
        user_requirements = {
            'TYPE': "Дипломная работа",
            'THEME': "Зарождение дипломатии в Древней Греции.",
            'WORK_SIZE': 67,
            'OTHER_REQUIREMENTS': "Гост",
            'INFORMATION_SOURCE': "Интернет",
            'ANY_INFORMATION': "Пропустить",
        }
        user_requirements['WORK_SIZE_MIN'] = user_requirements['WORK_SIZE'] * 1800
        user_requirements['WORK_SIZE_MAX'] = user_requirements['WORK_SIZE_MIN'] + 3600
        return user_requirements

    def test_OPENAI_API_KEY_import(self):
        """
        Проверяем, успешно ли импортирован OPENAI_API_KEY из .env.
        """
        key = os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty")
        self.assertTrue(key != "OPENAI_API_KEY is empty", "Ошибка при импорте OPENAI_API_KEY")

    def test_connection_to_open_ai(self):
        """
        Проверка соединения к API OpenAI.
        """
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
            ]
        )

        self.assertIsNotNone(response.choices[0].message.content)

    def test_plan_generation(self):
        """
        Проверка генерации плана.
        """
        # Тест прогоняется 10 раз
        iterations = 10
        for iteration in range(iterations):
            # Составление промпта пользователя
            user_prompt = promts.PLAN_PROMPT.format(
                THEME=self.user_requirements['THEME'],
                TYPE=self.user_requirements['TYPE'],
                WORK_SIZE_MIN=self.user_requirements['WORK_SIZE_MIN'],
                WORK_SIZE_MAX=self.user_requirements['WORK_SIZE_MAX'],
            )
            # Контекст сообщений для OpenAI.
            messages = [
                {"role": "system", "content": f"{promts.GENERAL_PROMPT}"},
                {"role": "user", "content": f"{user_prompt}"}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                response_format={"type": "json_object"},
                messages=messages,
            )

            plan = json.loads(response.choices[0].message.content)

            elements_counter = 0
            for element in plan:
                if element.startswith("Element-"):
                    elements_counter += 1
                    self.assertIsNotNone(plan[element]['Name'])
                    self.assertIsNotNone(plan[element]['Character capacity'])

            self.assertGreater(elements_counter, 3, f"Глав {elements_counter} < 3")
            print(f'Test_plan_generation(). {iteration + 1} iteration finished.')

    def test_document_creator(self):
        """
        Генерация документа.
        """
        plan = self.example_plan
        doc = Document()
        init_styles(doc)

        for element in plan:
            if element.startswith("Element-"):
                generation_text = ''

                user_chapter_prompt = promts.CHAPTER_PROMPT.format(
                    TYPE=self.user_requirements['TYPE'],
                    ELEMENT_NAME=plan[element]['Name'],
                    ELEMENT_NUM=element[8:],
                    CHAR_CAPPACITY=plan[element]['Character capacity'],
                )
                messages = [
                    {"role": "system", "content": f"{promts.GENERAL_PROMPT}"},
                    {"role": "user", "content": f"Plan: ```\n{self.example_plan}\n```"},
                    {"role": "user", "content": f"{user_chapter_prompt}"}
                ]
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo",
                    response_format={"type": "json_object"},
                    messages=messages,
                )
                chapter = json.loads(response.choices[0].message.content)
                print(f'chapter = {chapter}')
                generation_text += chapter['Content']

                generations = []
                print(f"generation_text: {generation_text}")
                while len(generation_text) < plan[element]['Character capacity']:
                    user_generation_prompt = promts.GENERATOR_PROMPT.format(
                        ELEMENT_NAME=plan[element]['Name'],
                        ELEMENT_NUM=element[8:],
                        CHAR_CAPPACITY=plan[element]['Character capacity'],
                    )
                    messages = [
                        {"role": "system", "content": f"{promts.GENERAL_PROMPT}"},
                        {"role": "user", "content": f"Plan: ```\n{self.example_plan}\n```"},
                        {"role": "user", "content": f"{user_chapter_prompt}"},
                        {"role": "assistant", "content": f"{chapter}"},
                        {"role": "user", "content": f"{user_generation_prompt}"},
                        *generations
                    ]
                    print(f"messages", messages)
                    response = self.client.chat.completions.create(
                        model="gpt-4-turbo",
                        response_format={"type": "json_object"},
                        messages=messages,
                    )
                    next_gen = json.loads(response.choices[0].message.content)
                    print(f'next_gen = {next_gen}')
                    generation_text += next_gen['Content']

                    generations.extend([
                        {"role": "assistant", "content": f"{next_gen}"},
                        {"role": "user", "content": f"{user_generation_prompt}"},
                    ])

                write_chapter(doc, plan[element]['Name'], generation_text, 1)
                break

        doc.save('document.docx')


if __name__ == '__main__':
    unittest.main()
