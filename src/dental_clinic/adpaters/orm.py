from typing import Dict
from domain import models
from util import initLog
from confluent_kafka.serialization import SerializationContext

logger = initLog(__name__)


schema_avro = """{
  "type": "record",
  "name": "UsuarioAccess",
  "fields": [
    {
      "name": "ID_REG",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "NM_USUARIO",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "CD_USUARIO",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "CD_UNID_ORG",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "DS_UNID_ORG",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "ID_PERFIL",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "NM_PERFIL",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "ST_USUARIO",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "CD_FUNCAO_SISTEMA",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "DS_FUNCAO_SISTEMA",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "DT_CONC_ACESSO",
      "type": ["null", "string"], "default": null
    },
    {
      "name": "HR_CONC_ACESSO",
      "type": ["null", "string"], "default": null
    }
  ]
}
"""


def dto_request_to_dict(cmd: models.UserDTO, context: SerializationContext) -> Dict[str, str]:
    return dict(
        ID_REG=cmd.ID_REG,
        NM_USUARIO=cmd.NM_USUARIO,
        CD_USUARIO=cmd.CD_USUARIO,
        CD_UNID_ORG=cmd.CD_UNID_ORG,
        DS_UNID_ORG=cmd.DS_UNID_ORG,
        ID_PERFIL=cmd.ID_PERFIL,
        NM_PERFIL=cmd.NM_PERFIL,
        ST_USUARIO=cmd.ST_USUARIO,
        CD_FUNCAO_SISTEMA=cmd.CD_FUNCAO_SISTEMA,
        DS_FUNCAO_SISTEMA=cmd.DS_FUNCAO_SISTEMA,
        DT_CONC_ACESSO=cmd.DT_CONC_ACESSO,
        HR_CONC_ACESSO=cmd.HR_CONC_ACESSO
    )
