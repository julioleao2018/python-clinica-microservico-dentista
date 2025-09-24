import re

from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timedelta

from rest.models import Usuarios, Clinicas, UsuariosClinicas, PerfisAcesso, Assinaturas, Planos
from utilities.seguranca import gerar_hash_senha, criar_token, TEMPO_EXPIRACAO_TOKEN

from fastapi import HTTPException

from util import initLog
logger = initLog(__name__)

# ========== Etapa 1: Criar Usuário ==========
def registrar_usuario(dados: dict, db: Session):
    try:
        if db.query(Usuarios).filter(Usuarios.email == dados["email"]).first():
            raise ValueError("Usuário já existe.")

        novo_usuario = Usuarios(
            nome=dados["nome"],
            email=dados["email"],
            senha_hash=gerar_hash_senha(dados["senha"]),
            ativo=True,
            criado_em=datetime.utcnow()
        )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)

        # token ainda não tem clinica_id
        token = criar_token({"sub": str(novo_usuario.usuario_id)})

        return {
            "usuario": {
                "id": str(novo_usuario.usuario_id),
                "nome": novo_usuario.nome,
                "email": novo_usuario.email
            },
            "access_token": token,
            "token_type": "bearer",
            "expires_in": TEMPO_EXPIRACAO_TOKEN
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError(f"Erro ao registrar usuário: {e}")


# ========== Etapa 2: Criar Clínica ==========
def registrar_clinica(dados: dict, usuario_id: str, db: Session):
    try:
        # normalizar CNPJ
        documento_limpo = re.sub(r"\D", "", dados["documento"])
        
        tipo_documento = dados.get("tipo_documento", "").upper()
        
        logger.info(f"dados: {dados}")
        logger.info(f"tipo documento: {tipo_documento}")
        
        if tipo_documento not in ["CNPJ", "CPF"]:
            raise HTTPException(status_code=400, detail="Tipo de documento inválido. Use CNPJ ou CPF.")

        nova_clinica = Clinicas(
            nome=dados["nome"],
            telefone=dados.get("telefone"),
            tipo_documento=tipo_documento,
            documento=documento_limpo,
            numero_profissionais=dados.get("numero_profissionais", 0),
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )
        db.add(nova_clinica)
        db.flush()  # gera clinica_id

        # garantir perfil admin
        perfil_admin = db.query(PerfisAcesso).filter(PerfisAcesso.nome == "admin").first()
        if not perfil_admin:
            perfil_admin = PerfisAcesso(nome="admin", descricao="Administrador da clínica")
            db.add(perfil_admin)
            db.flush()

        vinculo = UsuariosClinicas(
            usuario_id=usuario_id,
            clinica_id=nova_clinica.clinica_id,
            perfil_id=perfil_admin.perfil_id,
            criado_em=datetime.utcnow()
        )
        db.add(vinculo)

        # assinatura trial
        plano_trial = db.query(Planos).filter(Planos.nome == "Trial").first()
        if not plano_trial:
            plano_trial = Planos(
                nome="Trial",
                descricao="Plano de teste 7 dias",
                preco_mensal=0,
                dias_teste=7,
                ativo=True
            )
            db.add(plano_trial)
            db.flush()

        assinatura = Assinaturas(
            clinica_id=nova_clinica.clinica_id,
            plano_id=plano_trial.plano_id,
            data_inicio=datetime.utcnow(),
            data_fim=datetime.utcnow() + timedelta(days=plano_trial.dias_teste),
            status="trial"
        )
        db.add(assinatura)
        db.commit()

        # token com clinica_id agora
        token = criar_token({
            "sub": str(usuario_id),
            "clinica_id": str(nova_clinica.clinica_id)
        })

        # busca usuário no banco (garantia de dados atualizados)
        usuario = db.query(Usuarios).filter(Usuarios.usuario_id == usuario_id).first()

        return {
            "usuario": {
                "id": str(usuario.usuario_id),
                "nome": usuario.nome,
                "email": usuario.email
            },
            "clinica": {
                "id": str(nova_clinica.clinica_id),
                "nome": nova_clinica.nome
            },
            "assinatura": {
                "status": assinatura.status,
                "data_fim": assinatura.data_fim
            },
            "access_token": token,
            "token_type": "bearer",
            "expires_in": TEMPO_EXPIRACAO_TOKEN
        }

    except IntegrityError as e:
        db.rollback()
        if "clinicas_documento_key" in str(e.orig):
            raise HTTPException(status_code=409, detail="CNPJ já cadastrado.")
        raise HTTPException(status_code=400, detail="Erro de integridade ao registrar clínica.")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao registrar clínica.")