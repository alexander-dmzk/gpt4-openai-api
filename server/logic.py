import os

from gpt4_openai import ChatGptDriver


def get_stream_response(msg: str, model='gpt-4-browsing'):
    chatbot = ChatGptDriver(os.environ["OPENAI_SESSION_TOKEN"])
    try:
        return chatbot.send_message(msg, model=model)
    except Exception as e:
        print(str(e))
        chatbot.driver.save_screenshot('error.png')
        chatbot.close_driver()
        pid = os.getpid()
        os.kill(pid, 9)
        raise e
