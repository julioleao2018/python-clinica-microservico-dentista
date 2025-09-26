# rest/models/clinica_configuracoes.py
import uuid
from datetime import datetime
from sqlalchemy import Column, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from rest.database import Base

class ClinicaConfiguracoes(Base):
    __tablename__ = "clinica_configuracoes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clinica_id = Column(UUID(as_uuid=True), ForeignKey("clinicas.clinica_id", ondelete="CASCADE"), nullable=False)

    # Configurações
    email = Column(Text)
    fuso_horario = Column(Text, server_default="Brasília")
    logo_url = Column(Text)
    cep = Column(Text)
    endereco = Column(Text)
    numero = Column(Text)
    complemento = Column(Text)
    bairro = Column(Text)
    cidade = Column(Text)
    estado = Column(Text)

    # Features
    chat_interno = Column(Boolean, default=False)
    lista_espera = Column(Boolean, default=False)
    pesquisa_satisfacao = Column(Boolean, default=False)
    recebimento_tipo = Column(Text, server_default="clinic")

    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow)
    atualizado_em = Column(DateTime(timezone=True), default=datetime.utcnow)

    clinica = relationship("Clinicas", back_populates="configuracoes")