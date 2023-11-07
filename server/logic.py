import asyncio
import os

from gpt4_openai import ChatGptDriver


async def get_response(msg: str, model='gpt-4-browsing',
                       conversation_id='') -> str:
    chatbot = ChatGptDriver(os.environ["OPENAI_SESSION_TOKEN"],
                            model=model,
                            conversation_id=conversation_id)
    return await asyncio.to_thread(chatbot.send_message, msg)


async def get_stream_response(msg: str, model='gpt-4-browsing',
                              conversation_id=''):
    chatbot = ChatGptDriver(os.environ["OPENAI_SESSION_TOKEN"],
                            model=model,
                            conversation_id=conversation_id)
    return await asyncio.to_thread(chatbot.send_message, msg, stream=True)
