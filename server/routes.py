from fastapi import APIRouter

from server.logic import get_response

router = APIRouter(prefix='/api', tags=['main'])


@router.get('/sendMessage')
async def get_statistic(message: str):
    return await get_response(message)
