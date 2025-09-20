CREATE TABLE Usuarios (
    usuario_id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Perfis de Acesso
CREATE TABLE PerfisAcesso (
    perfil_id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    descricao TEXT
);

-- Tabela de Associação Usuário-Perfil
CREATE TABLE UsuarioPerfil (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    perfil_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(usuario_id),
    FOREIGN KEY (perfil_id) REFERENCES PerfisAcesso(perfil_id),
    UNIQUE (usuario_id, perfil_id)
);
