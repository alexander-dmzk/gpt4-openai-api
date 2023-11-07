import datetime
from typing import Literal

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from server.logic import get_stream_response

router = APIRouter(prefix='/api', tags=['main'])


@router.get('/sendMessageStream')
def send_message(message: str,
                  model: Literal[
                      'gpt-4-browsing',
                      'gpt-4-plugins',
                      'text-davinci-002-render-sha'
                  ]):
    print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
          f'request received: {message}')
    gen = get_stream_response(message, model)
    return EventSourceResponse(gen)
