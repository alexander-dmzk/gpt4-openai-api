import os

from gpt4_openai import ChatGptDriver


def get_stream_response(msg: str, model='gpt-4-browsing'):
    chatbot = ChatGptDriver(os.environ["OPENAI_SESSION_TOKEN"])
    return chatbot.send_message(msg, model=model)
