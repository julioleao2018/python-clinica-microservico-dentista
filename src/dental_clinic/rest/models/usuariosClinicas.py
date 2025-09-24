from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from rest.database import Base

class UsuariosClinicas(Base):
    __tablename__ = "usuarios_clinicas"

    id = Column(Integer, primary_key=True, autoincrement=True)

    usuario_id = Column(Integer, ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False)
    clinica_id = Column(Integer, ForeignKey("clinicas.clinica_id", ondelete="CASCADE"), nullable=False)
    perfil_id = Column(Integer, ForeignKey("perfis_acesso.perfil_id"), nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("usuario_id", "clinica_id", name="uq_usuario_clinica"),
    )

    # Relationships
    usuario = relationship("Usuarios", back_populates="clinicas")
    clinica = relationship("Clinicas", back_populates="usuarios")
    perfil = relationship("PerfisAcesso")