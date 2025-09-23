from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from rest.database import Base


class UsuariosClinicas(Base):
    __tablename__ = "usuarios_clinicas"

    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), primary_key=True)
    clinica_id = Column(UUID(as_uuid=True), ForeignKey("clinicas.clinica_id", ondelete="CASCADE"), primary_key=True)
    perfil_id = Column(Integer, ForeignKey("perfis_acesso.perfil_id"))
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow)

    usuario = relationship("Usuarios", back_populates="clinicas")
    clinica = relationship("Clinicas", back_populates="usuarios")
    perfil = relationship("PerfisAcesso")
