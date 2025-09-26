import uuid
from sqlalchemy import Column, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from rest.database import Base


class Clinicas(Base):
    __tablename__ = "clinicas"

    clinica_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(Text, nullable=False)
    telefone = Column(Text)
    tipo_documento = Column(Text, nullable=False, server_default="CNPJ")
    documento = Column(Text, unique=True)
    numero_profissionais = Column(Integer)
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow)
    atualizado_em = Column(DateTime(timezone=True), default=datetime.utcnow)

    usuarios = relationship("UsuariosClinicas", back_populates="clinica", cascade="all, delete")
    assinaturas = relationship("Assinaturas", back_populates="clinica")

    configuracoes = relationship("ClinicaConfiguracoes", back_populates="clinica", uselist=False, cascade="all, delete")