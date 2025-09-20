#! /usr/bin/python python3
from util import initLog
import uuid
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from starlette.responses import JSONResponse

import config
from rest import main_routes
from rest.errors import RestError

logger = initLog(__name__)

app = FastAPI(redoc_url="/v1/web/dental_clinic/redoc",
              title="dental_clinic",
              description="dental_clinic",
              version="v1")

origins = [
    "http://localhost",
    "http://localhost:8081",
    "http://localhost:8081/",
    "http://127.0.0.1:8081",
    "http://0.0.0.0:8081/"
    "http://0.0.0.0:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_routes.router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request.state.debug_id = str(uuid.uuid4())
    response = await call_next(request)
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return build_error_response(request, exc)


@app.exception_handler(Exception)
async def all_exceptions(request, exc):
    return build_error_response(request, exc)


def build_error_response(request, exc):
    logger.exception(exc)
    if not isinstance(exc, RestError):
        exc = RestError(exc, request=request)
    headers = {}
    if exc.headers:
        for header, value in exc.headers.items():
            headers[header] = value
    headers['Content-Type'] = 'application/json'
    return JSONResponse(
        exc.error.dict(),
        headers=headers,
        status_code=exc.statusCode
    )


if __name__ == '__main__':
    uvicorn.run(app,
                host='0.0.0.0',
                port=config.get_api_port())
