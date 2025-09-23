import uuid
from sqlalchemy import Column, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from rest.database import Base


class Assinaturas(Base):
    __tablename__ = "assinaturas"

    assinatura_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clinica_id = Column(UUID(as_uuid=True), ForeignKey("clinicas.clinica_id", ondelete="CASCADE"))
    plano_id = Column(Integer, ForeignKey("planos.plano_id"))
    data_inicio = Column(DateTime(timezone=True), default=datetime.utcnow)
    data_fim = Column(DateTime(timezone=True))
    status = Column(Text, default="trial")

    clinica = relationship("Clinicas", back_populates="assinaturas")
    plano = relationship("Planos", back_populates="assinaturas")
