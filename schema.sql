-- Tabela regional
CREATE TABLE IF NOT EXISTS regional (
    cd_regional BIGINT PRIMARY KEY,  
    nm_regional VARCHAR
);

-- Tabela bairro
CREATE TABLE IF NOT EXISTS bairro (
    cd_bairro BIGINT PRIMARY KEY,     
    nm_bairro VARCHAR,
    cd_regional BIGINT REFERENCES regional(cd_regional)  
);

-- Tabela setor_censitario
CREATE TABLE IF NOT EXISTS setor_censitario (
    cd_setor VARCHAR PRIMARY KEY,
    cd_bairro BIGINT REFERENCES bairro(cd_bairro),  
    situacao VARCHAR,
    area_km2 FLOAT
);

-- Tabela indicador_populacao 
CREATE TABLE IF NOT EXISTS indicador_populacao (
    cd_setor VARCHAR PRIMARY KEY REFERENCES setor_censitario(cd_setor),
    pop_total INTEGER,
    pop_masc INTEGER,
    pop_fem INTEGER
);