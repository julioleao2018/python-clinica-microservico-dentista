import os
import logging.config


class Constants:

    def __init__(self):
        self.CONST = {}


def setup():
    '''
    Metodo para extrair todas as variaveis de ambiente customizadas e remove-las
    Para acessar os dados utilizar
    from constants const
    cosnt[<A variavel que deseja usar>]

    '''
    global G_CONST
    G_CONST = Constants()
    G_CONST.CONST = {k: str_to_boolean(os.environ.get(k)) for k, v in os.environ.items() if k.startswith('APP') or 'TRACER' in k}
    for k,v in G_CONST.CONST.items():
        os.environ.pop(k)
    """
    Adicinar as configurações de logging baseados no utils/logging.yaml
    """
    logging.basicConfig(level=logging.INFO)


def get_product_name():
    return 'dental_clinic'

# conexoes em caso de Kafka
def get_broker_config():
    config = {'bootstrap.servers': G_CONST.CONST.get('APP_BROKER_SERVERS', 'localhost:9092'),
              'acks': 'all',
              'client.id': 'dental_clinic',
              'max.in.flight.requests.per.connection': 5,
              'debug': 'broker,topic,msg',
              'retries': 10000000,
              'sasl.mechanisms': 'PLAIN',
              'security.protocol': 'SASL_SSL',
              'sasl.username': G_CONST.CONST.get('APP_BROKER_USERNAME', '123'),
              'sasl.password': G_CONST.CONST.get('APP_BROKER_PASSWD', '456')
            }
    return config

# conexoes em caso de Kafka
def get_schema_registry_config():
    return {'url': G_CONST.CONST.get('APP_SCHEMA_REGISTRY_URL', 'http://localhost:8083'),
            'basic.auth.user.info': G_CONST.CONST.get('APP_SCHEMA_LOGIN', '123:acklakslk')
            }

def get_topic(): 
    return G_CONST.CONST.get('APP_TOPIC', 'topic')

def get_api_port():
    return int(G_CONST.CONST.get('APP_PORT', '8081'))

def get_api_url():
    host = G_CONST.CONST.get('APP_API_HOST', 'localhost')
    port = 5005 if host == 'localhost' else 80
    return f"http://{host}:{port}"

def get_postgres_db_username():
    return G_CONST.CONST.get('APP_POSTGRESQL_DB_USERNAME', '')

def get_postgres_db_password():
    return G_CONST.CONST.get('APP_POSTGRESQL_DB_PASSWORD', '')

def get_postgres_db_host():
    return G_CONST.CONST.get('APP_POSTGRESQL_DB_HOST', '')
    
def get_postgres_db_port():
    return G_CONST.CONST.get('APP_POSTGRESQL_DB_PORT', '')

def get_postgres_db_name():
    return G_CONST.CONST.get('APP_POSTGRESQL_DB_NAME', '')

def str_to_boolean(value):
    if isinstance(value, str):
        if value.lower() in ['true', 't', 'y', 'yes', 'yeah']:
            return True
        if value.lower() in ['false', 'f', 'n', 'no', 'nope']:
            return False
        return value
    else:
        return value