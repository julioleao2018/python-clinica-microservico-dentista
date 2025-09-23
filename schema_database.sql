-- ===========================================================
--  Pacote SQL Multi-Tenant SaaS - Clínica Odonto
-- ===========================================================

-- 1) Extensão para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===========================================================
-- 2) Usuários globais
-- ===========================================================
CREATE TABLE usuarios (
    usuario_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMPTZ,
    criado_em TIMESTAMPTZ DEFAULT now()
);

-- ===========================================================
-- 3) Perfis de acesso (roles globais)
-- ===========================================================
CREATE TABLE perfis_acesso (
    perfil_id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL,
    descricao TEXT
);

-- ===========================================================
-- 4) Clínicas (tenants)
-- ===========================================================
CREATE TABLE clinicas (
    clinica_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    telefone TEXT,
    tipo_documento TEXT CHECK (tipo_documento IN ('CNPJ', 'CPF')),
    documento TEXT UNIQUE, -- evita duplicar CNPJ/CPF
    numero_profissionais INT,
    criado_em TIMESTAMPTZ DEFAULT now(),
    atualizado_em TIMESTAMPTZ DEFAULT now()
);

-- ===========================================================
-- 5) Relação usuários <-> clínicas (multi-tenant)
-- ===========================================================
CREATE TABLE usuarios_clinicas (
    usuario_id UUID NOT NULL REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    clinica_id UUID NOT NULL REFERENCES clinicas(clinica_id) ON DELETE CASCADE,
    perfil_id INT NOT NULL REFERENCES perfis_acesso(perfil_id),
    criado_em TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (usuario_id, clinica_id)
);

CREATE INDEX idx_usuarios_clinicas_clinica ON usuarios_clinicas(clinica_id);

-- ===========================================================
-- 6) Planos (catálogo de planos)
-- ===========================================================
CREATE TABLE planos (
    plano_id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco_mensal NUMERIC(10,2) NOT NULL,
    dias_teste INT DEFAULT 7,
    ativo BOOLEAN DEFAULT TRUE
);

-- ===========================================================
-- 7) Assinaturas (cada clínica assina 1 plano por vez)
-- ===========================================================
CREATE TABLE assinaturas (
    assinatura_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES clinicas(clinica_id) ON DELETE CASCADE,
    plano_id INT NOT NULL REFERENCES planos(plano_id),
    data_inicio TIMESTAMPTZ DEFAULT now(),
    data_fim TIMESTAMPTZ,
    status TEXT CHECK (status IN ('trial', 'ativa', 'cancelada', 'expirada')) DEFAULT 'trial'
);

CREATE INDEX idx_assinaturas_clinica ON assinaturas(clinica_id);

-- ===========================================================
-- 8) Profissionais da clínica
-- ===========================================================
CREATE TABLE profissionais (
    profissional_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinica_id UUID NOT NULL REFERENCES clinicas(clinica_id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    funcao TEXT, -- dentista, auxiliar, recepção
    criado_em TIMESTAMPTZ DEFAULT now(),
    UNIQUE (clinica_id, email) -- o mesmo email pode existir em outra clínica
);

CREATE INDEX idx_profissionais_clinica ON profissionais(clinica_id);

-- ===========================================================
-- 9) Função para isolamento multi-tenant (RLS)
-- ===========================================================
CREATE OR REPLACE FUNCTION current_clinica_id()
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
  SELECT NULLIF(current_setting('app.clinica_id', true), '')::uuid
$$;

-- ===========================================================
-- 10) Row Level Security (RLS)
-- ===========================================================

-- Clínicas
ALTER TABLE clinicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE clinicas FORCE ROW LEVEL SECURITY;

CREATE POLICY p_clinicas_isolamento
ON clinicas
USING (clinica_id = current_clinica_id())
WITH CHECK (clinica_id = current_clinica_id());

-- Usuários_clinicas
ALTER TABLE usuarios_clinicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios_clinicas FORCE ROW LEVEL SECURITY;

CREATE POLICY p_usuarios_clinicas_isolamento
ON usuarios_clinicas
USING (clinica_id = current_clinica_id())
WITH CHECK (clinica_id = current_clinica_id());

-- Assinaturas
ALTER TABLE assinaturas ENABLE ROW LEVEL SECURITY;
ALTER TABLE assinaturas FORCE ROW LEVEL SECURITY;

CREATE POLICY p_assinaturas_isolamento
ON assinaturas
USING (clinica_id = current_clinica_id())
WITH CHECK (clinica_id = current_clinica_id());

-- Profissionais
ALTER TABLE profissionais ENABLE ROW LEVEL SECURITY;
ALTER TABLE profissionais FORCE ROW LEVEL SECURITY;

CREATE POLICY p_profissionais_isolamento
ON profissionais
USING (clinica_id = current_clinica_id())
WITH CHECK (clinica_id = current_clinica_id());

-- ===========================================================
-- Fim do pacote
-- ===========================================================
