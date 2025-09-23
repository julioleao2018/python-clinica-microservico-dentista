from sqlalchemy import Column, Integer, Text
from rest.database import Base


class PerfisAcesso(Base):
    __tablename__ = "perfis_acesso"

    perfil_id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(Text, unique=True, nullable=False)
    descricao = Column(Text)
