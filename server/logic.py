import os
import traceback

from gpt4_openai import GPT4OpenAI


async def get_response(msg: str) -> str:
    # Token is the __Secure-next-auth.session-token from chat.openai.com
    try:
        llm = GPT4OpenAI(token=os.environ["OPENAI_SESSION_TOKEN"],
                         headless=False,
                         model='gpt-4-browsing')
        # GPT3.5 will answer 8, while GPT4 should be smart enough to answer 10
        response = llm(msg)
        return response
    except Exception:
        response = traceback.format_exc()
        return response
