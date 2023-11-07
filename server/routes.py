import asyncio
from typing import Literal

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request

from server.logic import get_response, get_stream_response

router = APIRouter(prefix='/api', tags=['main'])


@router.get('/sendMessage')
async def get_statistic(message: str,
                        model: Literal[
                            'gpt-4-browsing',
                            'gpt-4-plugins',
                            'text-davinci-002-render-sha'
                        ],
                        conversation_id=''):
    return await get_response(message, model, conversation_id)


@router.get('/sendMessageStream')
async def get_statistic(message: str,
                        model: Literal[
                            'gpt-4-browsing',
                            'gpt-4-plugins',
                            'text-davinci-002-render-sha'
                        ],
                        request: Request,
                        conversation_id=''):
    gen = await get_stream_response(message, model, conversation_id)

    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            for i in gen:
                yield i

                await asyncio.sleep(0.1)
            break

    return EventSourceResponse(event_generator())
