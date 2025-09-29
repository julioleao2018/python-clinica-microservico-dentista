#! /usr/bin/python python3

import uuid
import uvicorn
import config
import traceback

from fastapi import FastAPI, Request, Depends, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from rest.database import get_db
from utilities.seguranca import verificar_token
from jose import jwt
from starlette.responses import JSONResponse
from util import initLog
from rest import main_routes
from rest.errors import RestError

logger = initLog(__name__)

app = FastAPI(redoc_url="/v1/web/dental_clinic/redoc",
              title="dental_clinic",
              description="dental_clinic",
              version="v1")

origins = [
    "http://localhost",
    "http://localhost:3000",   # Frontend Next.js local
    "http://localhost:8081",   # API local
    "http://127.0.0.1:8081",
    "http://0.0.0.0:8081",

    # Produção:
    "http://react-clinica-dental-site-sp.s3-website-sa-east-1.amazonaws.com",
    "https://clinica-alb-XXXXXXXX.sa-east-1.elb.amazonaws.com",  # seu ALB
    # depois, quando for mudar CloudFront/Route53:
    "https://d3j95xtv38y7ok.cloudfront.net"
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
async def set_tenant_header(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    request.state.usuario_id = None
    request.state.clinica_id = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            payload = verificar_token(token)
            request.state.usuario_id = payload.get("usuario_id")
            request.state.clinica_id = payload.get("clinica_id")
        except Exception as e:
            logger.warning(f"Token inválido ou expirado: {e}")

    response = await call_next(request)
    return response

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request.state.debug_id = str(uuid.uuid4())
    response = await call_next(request)
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erros = []
    for error in exc.errors():
        erros.append({
            "campo": ".".join(str(x) for x in error["loc"] if isinstance(x, (str, int))),
            "mensagem": error["msg"],
            "tipo": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "codigo": "VALIDATION_ERROR",
            "mensagem": "Erro de validação nos dados enviados.",
            "erros": erros
        }
    )
    
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "codigo": f"HTTP_{exc.status_code}",
            "mensagem": exc.detail,
            "erros": None
        }
    )

@app.exception_handler(Exception)
async def all_exceptions(request: Request, exc: Exception):
    # Aqui você pode logar o stacktrace completo
    logger.error(f"Erro inesperado: {exc}")
    logger.debug(traceback.format_exc())

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "codigo": "INTERNAL_SERVER_ERROR",
            "mensagem": "Ocorreu um erro inesperado. Tente novamente mais tarde.",
            "detalhes": None  # nunca retornar stacktrace para o cliente
        }
    )

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return build_error_response(request, exc)


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
