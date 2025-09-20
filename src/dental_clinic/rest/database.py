import config

config.setup()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from urllib.parse import quote_plus
from typing import Generator

# Configurações do banco
DB_USER = config.get_postgres_db_username()
DB_PASSWORD = quote_plus(config.get_postgres_db_password())
DB_HOST = config.get_postgres_db_host()
DB_PORT = config.get_postgres_db_port()
DB_NAME = config.get_postgres_db_name()

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Criando a engine síncrona
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "disable"},
    pool_pre_ping=True
)

# Criador de sessões síncronas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos ORM
Base = declarative_base()

# Dependency para injeção de sessão no FastAPI
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
