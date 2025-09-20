from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from domain.models import Usuarios
from utilities.seguranca import criar_token, gerar_hash_senha, verificar_senha, verificar_token, TEMPO_EXPIRACAO_TOKEN
from rest.database import get_db
from rest.models import UsuarioLogin, UsuarioResposta
from util import initLog
from datetime import datetime

router = APIRouter()
logger = initLog(__name__)



# Healthcheck
@router.get("/v1/web/dental_clinic/healthcheck", tags=["Sistema"], status_code=200)
def get_healthcheck():
    logger.info("Healthcheck solicitado")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "UP"})

# Login
@router.post("/v1/web/dental_clinic/login", tags=["Autenticação"])
def login(dados: UsuarioLogin = Body(...), db: Session = Depends(get_db)):
    try:
        usuario = db.query(Usuarios).filter(Usuarios.email == dados.email).first()
        if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
            logger.warning(f"Tentativa de login inválida para email: {dados.email}")
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        token = criar_token({"sub": str(usuario.usuario_id)})
        logger.info(f"Token gerado com sucesso para usuário: {usuario.email}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": TEMPO_EXPIRACAO_TOKEN
        }
    except SQLAlchemyError as e:
        logger.error(f"Erro ao realizar login: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")

# Criar usuário
@router.post("/v1/web/dental_clinic/usuarios", tags=["Autenticação"], response_model=UsuarioResposta)
def criar_usuario(dados: UsuarioLogin, db: Session = Depends(get_db)):
    try:
        if db.query(Usuarios).filter(Usuarios.email == dados.email).first():
            raise HTTPException(status_code=400, detail="Usuário já existe.")

        novo_usuario = Usuarios(
            nome=dados.email.split("@")[0],
            email=dados.email,
            senha_hash=gerar_hash_senha(dados.senha)
        )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)

        logger.info(f"Usuário criado com sucesso: {novo_usuario.email}")
        return novo_usuario

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Erro ao criar usuário: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao criar usuário")

# Rota protegida
@router.get("/v1/web/dental_clinic/privado", tags=["Protegido"])
def rota_protegida(usuario=Depends(verificar_token)):
    logger.info(f"Acesso autorizado ao usuário ID: {usuario['sub']}")
    return {"mensagem": f"Acesso permitido para o usuário ID: {usuario['sub']}"}
