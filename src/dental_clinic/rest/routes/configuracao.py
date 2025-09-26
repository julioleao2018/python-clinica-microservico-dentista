from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from rest.database import get_db
from rest.schemas.configuracao import ClinicaConfigRequest, ClinicaConfigResponse
from service_layer import configuracoes as service
from utilities.seguranca import verificar_token

router = APIRouter()

@router.get("/v1/web/dental_clinic/configuracoes", response_model=ClinicaConfigResponse, tags=["Configuração"],)
def get_config(db: Session = Depends(get_db), usuario=Depends(verificar_token)):
    return service.get_config(db, usuario["clinica_id"])


@router.put("/v1/web/dental_clinic/configuracoes", response_model=ClinicaConfigResponse, tags=["Configuração"],)
def update_config(dados: ClinicaConfigRequest, db: Session = Depends(get_db), usuario=Depends(verificar_token)):
    return service.update_config(db, usuario["clinica_id"], dados.dict(exclude_unset=True))


@router.post("/v1/web/dental_clinic/configuracoes/logo", response_model=ClinicaConfigResponse, tags=["Configuração"],)
def upload_logo(file: UploadFile = File(...), db: Session = Depends(get_db), usuario=Depends(verificar_token)):
    return service.upload_logo(db, usuario["clinica_id"], file)
