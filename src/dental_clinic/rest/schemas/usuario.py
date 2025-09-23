from pydantic import BaseModel, EmailStr

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class UsuarioResposta(BaseModel):
    usuario_id: int
    nome: str
    email: EmailStr

    class Config:
        from_attributes = True