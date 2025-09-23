from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from rest.models import Usuarios, Clinicas, UsuariosClinicas, PerfisAcesso, Assinaturas, Planos
from utilities.seguranca import gerar_hash_senha, criar_token, TEMPO_EXPIRACAO_TOKEN


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
        # criar clínica (só aceita CNPJ)
        nova_clinica = Clinicas(
            nome=dados["nome"],
            telefone=dados.get("telefone"),
            tipo_documento="CNPJ",
            documento=dados["documento"],
            numero_profissionais=dados.get("numero_profissionais", 0),
            criado_em=datetime.utcnow()
        )
        db.add(nova_clinica)
        db.flush()

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

        # token agora inclui clinica_id
        token = criar_token({
            "sub": str(usuario_id),
            "clinica_id": str(nova_clinica.clinica_id)
        })

        return {
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

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError(f"Erro ao registrar clínica: {e}")
