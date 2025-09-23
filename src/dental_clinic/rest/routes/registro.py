from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from rest.database import get_db
from service_layer.registro import registrar_usuario, registrar_clinica
from rest.schemas.registro import (
    RegistroUsuarioRequest, RegistroUsuarioResponse,
    RegistroClinicaRequest, RegistroClinicaResponse
)
from utilities.seguranca import verificar_token

router = APIRouter()


# ========== Etapa 1: Criar Usuário ==========
@router.post("/v1/web/dental_clinic/registro/usuario",
             tags=["Registro"],
             response_model=RegistroUsuarioResponse)
def registro_usuario(dados: RegistroUsuarioRequest = Body(...),
                     db: Session = Depends(get_db)):
    try:
        return registrar_usuario(dados.dict(), db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Etapa 2: Criar Clínica ==========
@router.post("/v1/web/dental_clinic/registro/clinica",
             tags=["Registro"],
             response_model=RegistroClinicaResponse)
def registro_clinica(dados: RegistroClinicaRequest = Body(...),
                     db: Session = Depends(get_db),
                     usuario=Depends(verificar_token)):
    try:
        return registrar_clinica(dados.dict(), usuario["usuario_id"], db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
