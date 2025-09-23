import uuid
from sqlalchemy import Column, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from rest.database import Base


class Usuarios(Base):
    __tablename__ = "usuarios"

    usuario_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    senha_hash = Column(Text, nullable=False)
    ativo = Column(Boolean, default=True)
    ultimo_login = Column(DateTime(timezone=True))
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow)

    clinicas = relationship("UsuariosClinicas", back_populates="usuario")