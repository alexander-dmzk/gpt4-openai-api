import os

from gpt4_openai import ChatGptDriver


async def get_response(msg: str, model='gpt-4-browsing') -> str:
    chatbot = ChatGptDriver(os.environ["OPENAI_SESSION_TOKEN"],
                            model=model)
    return chatbot.send_message(msg)


async def get_stream_response(msg: str, model='gpt-4-browsing'):
    chatbot = ChatGptDriver(os.environ["OPENAI_SESSION_TOKEN"],
                            model=model)
    return chatbot.send_message(msg, stream=True)
