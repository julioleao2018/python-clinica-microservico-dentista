# Etapa de build
FROM python:3.10.10-alpine3.17 AS build

LABEL maintainer="julio.leaojc5@gmail.com"

ARG DB_HOST
ARG DB_PORT
ARG DB_USER
ARG DB_PASSWORD
ARG DB_NAME

ENV APP_POSTGRESQL_DB_HOST=$DB_HOST \
    APP_POSTGRESQL_DB_PORT=$DB_PORT \
    APP_POSTGRESQL_DB_USERNAME=$DB_USER \
    APP_POSTGRESQL_DB_PASSWORD=$DB_PASSWORD \
    APP_POSTGRESQL_DB_NAME=$DB_NAME

# Instalar dependências de build necessárias
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    build-base \
    postgresql-dev \
    python3-dev \
    cargo

RUN pip install --upgrade pip

# Etapa final
FROM python:3.10.10-alpine3.17 AS runtime

RUN apk add --no-cache \
    libpq \
    curl \
    postgresql-client

# Criar usuário de execução
RUN adduser -D worker
USER worker

# Define diretório de trabalho
WORKDIR /home/worker

# Caminho do pip user
ENV PATH="/home/worker/.local/bin:${PATH}"

# Copiar dependências e código
COPY --from=build /usr/local /usr/local
COPY requirements.txt /tmp/requirements.txt
COPY src/ /home/worker/src/
COPY --chown=worker:worker . .

# Instalar dependências
RUN pip install --user -r /tmp/requirements.txt

# Entrar no diretório do app
WORKDIR /home/worker/src/dental_clinic

# Comando padrão do container
CMD ["uvicorn", "fast_app:app", "--host", "0.0.0.0", "--port", "8081"]
