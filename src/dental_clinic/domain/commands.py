# pylint: disable=too-few-public-methods
from dataclasses import dataclass
from typing import List, Optional
from domain.models import UserDTO

class Command:
    pass

@dataclass
class SendMessageKafka(Command):
    users: List[UserDTO]
