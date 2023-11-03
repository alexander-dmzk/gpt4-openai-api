from typing import Literal

from fastapi import APIRouter

from server.logic import get_response

router = APIRouter(prefix='/api', tags=['main'])


@router.get('/sendMessage')
async def get_statistic(message: str,
                        model: Literal[
                            'gpt-4-browsing',
                            'gpt-4-plugins',
                            'text-davinci-002-render-sha'
                        ]):
    return await get_response(message, model)
