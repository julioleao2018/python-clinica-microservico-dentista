# service_layer/configuracoes.py
import os

from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from rest.models import Clinicas, ClinicaConfiguracoes
from rest.schemas.configuracao import ClinicaConfigResponse
from util import initLog

from infra.s3_storage import (
    make_logo_key,
    upload_fileobj,
    delete_object_safe,
    public_url,
    presigned_url,
)

logger = initLog(__name__)

CAMPOS_CLINICAS = [
    "nome", "telefone", "documento", "tipo_documento", "numero_profissionais",
]

CAMPOS_CONFIG = [
    "email", "fuso_horario", "logo_url",
    "cep", "endereco", "numero", "complemento", "bairro", "cidade", "estado",
    "chat_interno", "lista_espera", "pesquisa_satisfacao", "recebimento_tipo",
]

# ---------- NEW: resolve URL de retorno a partir do que está no banco ----------
def _resolve_logo_return_url(stored_value: str | None) -> str | None:
    """
    Se armazenamos um 'key' do S3, devolve URL pública ou pré-assinada.
    Se já estiver uma URL (http), retorna como está.
    """
    if not stored_value:
        return None
    if stored_value.startswith("http://") or stored_value.startswith("https://"):
        return stored_value  # compatibilidade com versões antigas
    # trata como key do S3
    return public_url(stored_value) or presigned_url(stored_value, expires_seconds=3600)

def _to_response(clinica: Clinicas, config: ClinicaConfiguracoes | None) -> ClinicaConfigResponse:
    return ClinicaConfigResponse(
        clinica_id=str(clinica.clinica_id),
        nome=clinica.nome,
        telefone=clinica.telefone,
        documento=clinica.documento,
        tipo_documento=clinica.tipo_documento,
        numero_profissionais=clinica.numero_profissionais,
        criado_em=clinica.criado_em,
        atualizado_em=clinica.atualizado_em,

        email=(config.email if config else None),
        fuso_horario=(config.fuso_horario if config else None),

        # ---------- NEW: logo_url resolvida para o front ----------
        logo_url=_resolve_logo_return_url(config.logo_url if config else None),

        cep=(config.cep if config else None),
        endereco=(config.endereco if config else None),
        numero=(config.numero if config else None),
        complemento=(config.complemento if config else None),
        bairro=(config.bairro if config else None),
        cidade=(config.cidade if config else None),
        estado=(config.estado if config else None),

        chat_interno=(config.chat_interno if config else False),
        lista_espera=(config.lista_espera if config else False),
        pesquisa_satisfacao=(config.pesquisa_satisfacao if config else False),
        recebimento_tipo=(config.recebimento_tipo if config else "clinic"),
    )

def get_config(db: Session, clinica_id: str) -> ClinicaConfigResponse:
    try:
        clinica = db.query(Clinicas).filter_by(clinica_id=clinica_id).first()
        if not clinica:
            logger.warning(f"[CONFIG] Clínica {clinica_id} não encontrada")
            raise HTTPException(status_code=404, detail="Clínica não encontrada")

        config = db.query(ClinicaConfiguracoes).filter_by(clinica_id=clinica_id).first()

        if not config:
            config = ClinicaConfiguracoes(clinica_id=clinica_id)
            db.add(config)
            db.commit()
            db.refresh(config)
            logger.info(f"[CONFIG] Configuração criada para clínica {clinica_id}")

        logger.info(f"[CONFIG] Configuração consolidada carregada para clínica {clinica_id}")
        return _to_response(clinica, config)

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"[CONFIG] Erro ao buscar configuração consolidada da clínica {clinica_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar configurações")

def update_config(db: Session, clinica_id: str, dados: dict) -> ClinicaConfigResponse:
    try:
        clinica = db.query(Clinicas).filter_by(clinica_id=clinica_id).first()
        if not clinica:
            logger.warning(f"[CONFIG] Clínica {clinica_id} não encontrada")
            raise HTTPException(status_code=404, detail="Clínica não encontrada")

        config = db.query(ClinicaConfiguracoes).filter_by(clinica_id=clinica_id).first()
        if not config:
            config = ClinicaConfiguracoes(clinica_id=clinica_id)
            db.add(config)

        for campo in CAMPOS_CLINICAS:
            if campo in dados:
                setattr(clinica, campo, dados[campo])

        for campo in CAMPOS_CONFIG:
            if campo in dados:
                setattr(config, campo, dados[campo])

        config.atualizado_em = datetime.utcnow()

        db.commit()
        db.refresh(clinica)
        db.refresh(config)

        logger.info(f"[CONFIG] Clínica + Config atualizadas para clínica {clinica_id}")
        return _to_response(clinica, config)

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"[CONFIG] Erro ao atualizar clínica/configuração {clinica_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar configurações")

# -------------------- REFATORADO: upload para S3 com boto3 --------------------
def upload_logo(db: Session, clinica_id: str, file: UploadFile) -> ClinicaConfigResponse:
    try:
        # valida clinic
        clinica = db.query(Clinicas).filter_by(clinica_id=clinica_id).first()
        if not clinica:
            raise HTTPException(status_code=404, detail="Clínica não encontrada")

        # valida tipo e tamanho básicos
        allowed = {"image/png", "image/jpeg", "image/webp", "image/svg+xml"}
        if file.content_type not in allowed:
            raise HTTPException(status_code=400, detail="Formato de imagem não suportado")

        # posiciona no início (por garantia)
        file.file.seek(0)

        # gera key única
        key = make_logo_key(clinica_id, file.filename)

        # upload pro S3 (público ou privado conforme env)
        upload_fileobj(file.file, key, content_type=file.content_type)

        # busca/instancia config
        config = db.query(ClinicaConfiguracoes).filter_by(clinica_id=clinica_id).first()
        if not config:
            config = ClinicaConfiguracoes(clinica_id=clinica_id)
            db.add(config)

        # apaga anterior se for um key (não URL http)
        old = config.logo_url
        if old and not (old.startswith("http://") or old.startswith("https://")):
            delete_object_safe(old)

        # armazenamos SOMENTE o key do S3
        config.logo_url = key
        config.atualizado_em = datetime.utcnow()

        db.commit()
        db.refresh(clinica)
        db.refresh(config)

        # devolvemos URL resolvida (pública ou pré-assinada)
        resolved_url = _resolve_logo_return_url(config.logo_url)

        logger.info(f"[CONFIG] Logo atualizado para clínica {clinica_id}: {key}")
        # monta a resposta com o resolved_url
        resp = _to_response(clinica, config)
        resp.logo_url = resolved_url
        return resp

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"[CONFIG] Erro de banco ao salvar logo da clínica {clinica_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar logo")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[CONFIG] Erro inesperado ao salvar logo da clínica {clinica_id}")
        raise HTTPException(status_code=500, detail="Falha inesperada ao salvar logo")
