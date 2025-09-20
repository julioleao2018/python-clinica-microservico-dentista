from rest.errors import ResponseError
from spec.messages import *


get_health_check = {200: {"model": None, "description": health_message},
                       500: {"model": ResponseError, "description": error_500}
                       }

save_extrato = {202: {"model": None, "description": extrato_success},
                 400: {"model": ResponseError, "description": error_400},
                 500: {"model": ResponseError, "description": error_500}
                 }

get_extrato = {200: {"model": None, "description": get_success},
                 400: {"model": ResponseError, "description": error_400},
                 500: {"model": ResponseError, "description": error_500}
                 }