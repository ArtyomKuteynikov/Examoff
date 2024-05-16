import asyncio

from openai import OpenAI
import os
from openai import AssistantEventHandler
from dotenv import load_dotenv

from gateway.chat.dependens.answers import open_free_sate_message_in_websockets, send_free_sate_message_in_websockets

load_dotenv()
# Замените 'YOUR_OPENAI_API_KEY' на ваш API-ключ
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY is empty"))


# Upload a file with an "assistants" purpose


def upload_file_in_openai(file_path):
    file = client.files.create(
        file=open(file_path, "rb"),
        purpose='assistants'
    )
    return file


def create_openai_assistant():
    assistant = client.beta.assistants.create(
        name="Знающий все студент",
        instructions="Ты являешься студентом, ты написал работу, и сейчас тебе по ней задают вопросы на экзамене.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )
    return assistant


def upload_vector_store(file_paths):
    vector_store = client.beta.vector_stores.create(name="Работа на экзамене")
    file_streams = [open(path, "rb") for path in file_paths]
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )
    return vector_store


def create_open_ai_thread(assistant, vector_store, messages):
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )
    thread = client.beta.threads.create(messages=messages)
    return thread


class EventHandler(AssistantEventHandler):
    def __init__(self, chat, connections):
        super().__init__()
        self.chat = chat
        self.connections = connections
        self.full_message = ''

    def on_text_created(self, text) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(open_free_sate_message_in_websockets(self.connections, self.chat))

    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
        self.full_message += delta.value

        loop = asyncio.get_event_loop()
        loop.create_task(send_free_sate_message_in_websockets(
            self.connections,
            self.chat,
            delta.value,
            ''
        ))


def on_tool_call_created(self, tool_call):
    print(f"\nassistant on_tool_call_created> {tool_call.type}\n", flush=True)


def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
        if delta.code_interpreter.input:
            print(delta.code_interpreter.input, end="", flush=True)
        if delta.code_interpreter.outputs:
            print(f"\n\noutput on_tool_call_delta>", flush=True)
            for output in delta.code_interpreter.outputs:
                if output.type == "logs":
                    loop = asyncio.get_event_loop()
                    loop.create_task(
                        send_free_sate_message_in_websockets(
                            self.connections,
                            self.chat,
                            delta.value,
                            'stop'
                        ))
