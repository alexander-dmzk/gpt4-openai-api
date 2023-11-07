from typing import Literal

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from server.logic import get_response, get_stream_response

router = APIRouter(prefix='/api', tags=['main'])


@router.get('/sendMessageStream')
def get_statistic(message: str,
                  model: Literal[
                      'gpt-4-browsing',
                      'gpt-4-plugins',
                      'text-davinci-002-render-sha'
                  ]):
    gen = get_stream_response(message, model)
    return EventSourceResponse(gen)
