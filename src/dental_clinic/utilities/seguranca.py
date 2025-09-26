from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Hash de senha
pwd_context = CryptContext(
    schemes=["argon2", "pbkdf2_sha256"],
    default="argon2",
    deprecated="auto"
)

def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plain, senha_hash)

# JWT
SECRET_KEY = "b1Mj7amXTU1XK1_qo4KG29sF7jbad0VLfS9ppuyFtXckVF5KhS-JR7Sj0O8rU4jvMJNXTHjdFwVkYsIOzmdYpw"
ALGORITHM = "HS256"
EXPIRA_MINUTOS = 60
TEMPO_EXPIRACAO_TOKEN = 3600  # segundos

def criar_token(dados: dict):
    to_encode = dados.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRA_MINUTOS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/web/dental_clinic/login")

def verificar_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        clinica_id: str = payload.get("clinica_id")  # pode ser None no início

        if usuario_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "usuario_id": usuario_id,
            "clinica_id": clinica_id
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
def verificar_token_com_clinica(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        clinica_id: str | None = payload.get("clinica_id")

        if usuario_id is None or clinica_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: é necessário estar vinculado a uma clínica.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "usuario_id": usuario_id,
            "clinica_id": clinica_id
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
