import os
from argparse import ArgumentParser
from datetime import datetime
from typing import Literal

import uvicorn
from fastapi import FastAPI
from sse_starlette import EventSourceResponse
from starlette.responses import Response

from server.logic import get_stream_response

app = FastAPI(docs_url='/')


@app.get('/api/sendMessageStream')
def send_message(message: str,
                 model: Literal[
                     'gpt-4-browsing',
                     'gpt-4-plugins',
                     'text-davinci-002-render-sha'
                 ]):
    print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
          f'request received: {message}')
    gen = get_stream_response(message, model)
    return EventSourceResponse(gen)


@app.get('/healthcheck')
async def healthcheck():
    return Response(status_code=200)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument("--host", "-H", type=str,
                           default='0.0.0.0',
                           help="scrapers api server host")
    argparser.add_argument("--port", "-P", type=int,
                           default=3000,
                           help="scrapers api server port")
    args = argparser.parse_args()
    uvicorn.run("server.instance:app", host=args.host, port=args.port)
