from sqlalchemy import Column, Integer, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from rest.database import Base


class Planos(Base):
    __tablename__ = "planos"

    plano_id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(Text, nullable=False)
    descricao = Column(Text)
    preco_mensal = Column(Numeric(10, 2), nullable=False)
    dias_teste = Column(Integer, default=7)
    ativo = Column(Boolean, default=True)

    assinaturas = relationship("Assinaturas", back_populates="plano")
