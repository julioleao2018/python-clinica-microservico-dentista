# pylint: disable=broad-except, attribute-defined-outside-init
from __future__ import annotations
from typing import Callable, Dict, List, Union, Type, TYPE_CHECKING
from domain import commands
from util import initLog

if TYPE_CHECKING:
    from . import unit_of_work

logger = initLog(__name__)

Message = [commands.Command]

class MessageBus:

    def __init__(
        self,
        uow: unit_of_work.AbstractUnitOfWork,
        command_handlers: Dict[Type[commands.Command], Callable],
    ):
        self.uow = uow
        self.command_handlers = command_handlers

    def handle(self, message: Message):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, commands.Command):
                self.handle_command(message)
            else:
                raise Exception(f'{message} was not an Command')

    def handle_command(self, command: commands.Command):
        logger.debug('handling command %s', command)
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
        except Exception:
            logger.exception('Exception handling command %s', command)
            raise
