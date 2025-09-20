# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
import config
from adpaters import repository
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient


class AbstractUnitOfWork(abc.ABC):
    repository: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = Producer(config.get_broker_config())
DEFAULT_SCHEMA_SESSION = SchemaRegistryClient(conf=config.get_schema_registry_config())


class KafkaUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY,
                 schema_factory=DEFAULT_SCHEMA_SESSION):
        self.session_factory = session_factory
        self.schema_factory = schema_factory
        
    def __enter__(self):
        self.session = self.session_factory  # type: Producer
        self.repository = repository.KafkaRepository(self.session, self.schema_factory)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.flush()

    def _commit(self):
        self.session.flush()

    def rollback(self):
        pass
