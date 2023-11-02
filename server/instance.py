from argparse import ArgumentParser

import uvicorn
from fastapi import FastAPI
from starlette.responses import Response

from server.routes import router

app = FastAPI(docs_url='/')
app.include_router(router)


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
