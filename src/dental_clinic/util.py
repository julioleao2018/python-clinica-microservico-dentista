from dataclasses import fields, _MISSING_TYPE
import logging
from typing import Any, Optional
from collections.abc import Iterable
from typing import Any, Optional
from dataclasses import make_dataclass, Field
import pydantic
from pythonjsonlogger import jsonlogger
from datetime import datetime
import pytz

brazil_tz = pytz.timezone('America/Sao_Paulo')

def convert_flat_dataclass_to_pydantic(
    dcls: type, name: Optional[str] = None
) -> type[pydantic.BaseModel]:
    if name is None:
        name_ = f"Pydantic{dcls.__name__}"
    else:
        name_ = name
    return pydantic.create_model(  # type: ignore
        name_,
        **_get_pydantic_field_kwargs(dcls),
    )


def _get_pydantic_field_kwargs(dcls: type) -> dict[str, tuple[type, Any]]:
    # get attribute names and types from dataclass into pydantic format
    pydantic_field_kwargs = dict()
    for _field in fields(dcls):
        # check is field has default value
        if isinstance(_field.default, _MISSING_TYPE):
            # no default
            default = ...
        else:
            default = _field.default

        pydantic_field_kwargs[_field.name] = (_field.type, default)
    return pydantic_field_kwargs


def convert_flat_pydantic_to_dataclass(
    pydantic_cls: type[pydantic.BaseModel],
    name: Optional[str] = None,
    slots: bool = True,
) -> type:
    if name is None:
        name_ = f"DataClass{pydantic_cls.__name__}"
    else:
        name_ = name
    return make_dataclass(
        name_,
        _get_dataclass_fields(pydantic_cls),
        slots=slots,
    )


def _get_dataclass_fields(
    pydantic_cls: type[pydantic.BaseModel],
) -> Iterable[str | tuple[str, type] | tuple[str, type, Field[Any]]]:
    # get attribute names and types from pydantic into dataclass format
    dataclass_fields = []
    for _field in pydantic_cls.__fields__.values():
        if _field.required:
            field_tuple = (_field.name, _field.type_)
        else:
            field_tuple = (  # type: ignore
                _field.name,
                _field.type_,
                _field.default,
            )

        dataclass_fields.append(field_tuple)
    return dataclass_fields



def initLog(name, leve=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # log_formatter = logging.Formatter("%(filename)s %(funcName)s %(lineno)s %(asctime)s %(levelname)s %(name)s %(message)s")
    log_formatter = jsonlogger.JsonFormatter('%(filename)s %(funcName)s %(lineno)s %(asctime)s %(levelname)s %(name)s %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    return logger

def oracle_format_string(string: str, length: int = 0):
    string = string.strip()

    if length > 0 and len(string) > length: raise Exception(f"Tamanho do campo inválido valor: {string} tamanho: {length}")

    return string

def oracle_current_date():
    date_obj = datetime.now(brazil_tz)
    formatted_date = date_obj.strftime('%d/%m/%y %H:%M:%S')
    # formatted_date = date_obj.strftime('%Y-%m-%d')
    return datetime.strptime(formatted_date, '%d/%m/%y %H:%M:%S')
    

def oracle_format_date(date):
    try:
        if date == "": return None
        date_obj = datetime.strptime(date, '%Y/%m/%d')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return datetime.strptime(formatted_date, "%Y-%m-%d")
    except:
        return None

def oracle_format_date_invert(date):
    try:
        if date == "": return None
        date_obj = datetime.strptime(date, "%d/%m/%y")
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return datetime.strptime(formatted_date, "%Y-%m-%d")
    except:
        return None

def oracle_format_float(str_float: str, length: int = 0):
    str_float = str_float.strip()
    if str_float == "": str_float = "0"

    if length > 0 and len(str_float) > length: raise Exception(f"Tamanho do campo inválido valor: {str_float} tamanho: {length}")

    try:
        return float(str_float) if str_float else None
    except:
        return None

def oracle_format_int(str_int: str, length: int = 0):
    str_int = str_int.strip()
    if str_int == "": str_int = "0"

    if length > 0 and len(str_int) > length: raise Exception(f"Tamanho do campo inválido valor: {str_int} tamanho: {length}")

    try:
        return int(str_int) if str_int else None
    except:
        return None

def oracle_format_bool(str_bool):
    try:
        return bool(str_bool) if str_bool else None
    except:
        return None

def initLog(name, leve=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # log_formatter = logging.Formatter("%(filename)s %(funcName)s %(lineno)s %(asctime)s %(levelname)s %(name)s %(message)s")
    log_formatter = jsonlogger.JsonFormatter('%(filename)s %(funcName)s %(lineno)s %(asctime)s %(levelname)s %(name)s %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    return logger