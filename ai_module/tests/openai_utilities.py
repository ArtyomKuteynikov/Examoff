import unittest
from dotenv import load_dotenv
import os

from ai_module.openai_utilities.openai_api_client import create_openai_completion
from ai_module.schemas.message import SystemMessage, UserMessage, AssistantMessage, messages_to_openai_format

load_dotenv()


class OpenAIUtilities(unittest.TestCase):

    def init_messages(self):
        """
        Готовый список сообщений.
        """
        system_message = SystemMessage(content="You are helpful assistant.")
        user_message = UserMessage(content="Hello")
        assistant_message = AssistantMessage(content="Hello! How are you?")

        return [system_message, user_message, assistant_message]

    def test_OPENAI_API_KEY_import(self):
        """
        Проверяем, успешно ли импортирован OPENAI_API_KEY из .env.
        """
        key = os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty")
        self.assertTrue(key != "OPENAI_API_KEY is empty", "Ошибка при импорте OPENAI_API_KEY")

    def test_messages_to_openai_format(self):
        """
        Проверка корректности перевода в формат OpenAI.
        """
        messages = self.init_messages()

        expected_result = [
            {'role': 'system', 'content': 'You are helpful assistant.'},
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hello! How are you?'}
        ]
        self.assertEqual(messages_to_openai_format(messages), expected_result, "Ошибка структуры.")

    def test_create_openai_completion(self):
        """
        Проверка генерации текста от OpenAI.
        """
        messages = self.init_messages()
        self.assertTrue(create_openai_completion(model="gpt-3.5-turbo-0613", messages=messages))


if __name__ == '__main__':
    unittest.main()
