import re
from pydantic import BaseModel, EmailStr, field_validator, constr
from typing import Optional
from datetime import datetime


# ========== Requisição Etapa 1: Usuário ==========
class RegistroUsuarioRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str

    @field_validator("senha")
    def validar_senha(cls, v):
        if len(v) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r"[a-z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r"[0-9]", v):
            raise ValueError("A senha deve conter pelo menos um número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("A senha deve conter pelo menos um caractere especial.")
        return v


class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str


class RegistroUsuarioResponse(BaseModel):
    usuario: UsuarioResponse
    access_token: str
    token_type: str
    expires_in: int


# ========== Requisição Etapa 2: Clínica ==========
class RegistroClinicaRequest(BaseModel):
    nome: str
    telefone: Optional[str]
    tipo_documento: str  # "CNPJ" ou "CPF"
    documento: str
    numero_profissionais: Optional[int]

class ClinicaResponse(BaseModel):
    id: str
    nome: str


class AssinaturaResponse(BaseModel):
    status: str
    data_fim: datetime


class RegistroClinicaResponse(BaseModel):
    clinica: ClinicaResponse
    assinatura: AssinaturaResponse
    access_token: str
    token_type: str
    expires_in: int
