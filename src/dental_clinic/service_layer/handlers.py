# pylint: disable=unused-argument
from __future__ import annotations
from typing import Dict, Callable, Type, TYPE_CHECKING
from domain import commands, models
from util import initLog

logger = initLog(__name__)

if TYPE_CHECKING:
    from . import unit_of_work

def handle_kafka(
    cmd: commands.SendMessageKafka, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        for user in cmd.users:
            uow.repository.add(user)
        uow.commit()

COMMAND_HANDLERS = {
    commands.SendMessageKafka: handle_kafka 
}  # type: Dict[Type[commands.Command], Callable]
