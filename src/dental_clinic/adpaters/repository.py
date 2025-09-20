import abc
import config
from adpaters import orm
from domain import models
from uuid import uuid4
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from util import initLog

logger = initLog(__name__)

class AbstractRepository(abc.ABC):

    def __init__(self):
        pass

    def add(self, entity):
        self._add(entity)

    @abc.abstractmethod
    def _add(self, entity):
        raise NotImplementedError
    
class KafkaRepository(AbstractRepository):
    def __init__(self, session, schema_session):
        super().__init__()
        self.session = session
        self.schema_session = schema_session

    def _add(self, message: models.UserDTO):
        self.session.poll(0)  # Polling para servir as callbacks do delivery report

        # Cria o AvroSerializer usando o schema
        avro_serializer = AvroSerializer(
            self.schema_session,
            orm.schema_avro,
            orm.dto_request_to_dict  # Função para serializar os dados
        )

        # Serializa a chave como string
        string_serializer = StringSerializer('utf_8')

        logger.debug('********### LOG SESSION %s', self.schema_session)
        logger.debug('********### LOG TOPIC %s', config.get_topic())
        logger.debug('********### LOG REPORT %s', self.delivery_report)

        # Produzindo a mensagem para o Kafka
        self.session.produce(
            topic=config.get_topic(),  # Tópico do Kafka
            key=string_serializer(str(uuid4())),  # Gera um UUID como chave
            value=avro_serializer(message, SerializationContext(config.get_topic(), MessageField.VALUE)),
            on_delivery=self.delivery_report  # Callback para relatar sucesso/falha
        )

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')
