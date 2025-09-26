from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ClinicaConfigRequest(BaseModel):
    # Dados de contato
    email: Optional[str]
    
    # Endereço
    cep: Optional[str]
    endereco: Optional[str]
    numero: Optional[str]
    complemento: Optional[str]
    bairro: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]

    # Configurações
    fuso_horario: Optional[str]
    logo_url: Optional[str]

    # Recursos
    chat_interno: bool = False
    lista_espera: bool = False  
    pesquisa_satisfacao: bool = False

    # Contabilidade
    recebimento_tipo: str = "clinic" 

class ClinicaConfigResponse(BaseModel):
    id: Optional[str] = None
    clinica_id: UUID

    nome: Optional[str]
    telefone: Optional[str]
    documento: Optional[str]
    tipo_documento: Optional[str]
    numero_profissionais: Optional[int]

    email: Optional[str]
    fuso_horario: Optional[str]
    logo_url: Optional[str]

    cep: Optional[str]
    endereco: Optional[str]
    numero: Optional[str]
    complemento: Optional[str]
    bairro: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]

    chat_interno: bool = False
    lista_espera: bool = False
    pesquisa_satisfacao: bool = False
    recebimento_tipo: str = "clinic"

    criado_em: Optional[datetime]
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True