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
    pop_fem INTEGER,
    pop_0_4 INTEGER,
    pop_5_9 INTEGER,
    pop_10_14 INTEGER,
    pop_15_19 INTEGER,
    pop_20_24 INTEGER,
    pop_25_29 INTEGER,
    pop_30_39 INTEGER,
    pop_40_49 INTEGER,
    pop_50_59 INTEGER,
    pop_60_69 INTEGER,
    pop_70_mais INTEGER
);

CREATE TABLE IF NOT EXISTS indicador_alfabetizacao (
    cd_setor VARCHAR PRIMARY KEY REFERENCES setor_censitario(cd_setor),

    -- alfabetizados/não alfabetizados por faixa etária
    alf_15_29 INTEGER,
    nao_alf_15_29 INTEGER,
    alf_30_59 INTEGER,
    nao_alf_30_59 INTEGER,
    alf_60_mais INTEGER,
    nao_alf_60_mais INTEGER,

    -- totais por sexo (+15)
    total_masc_alf INTEGER,
    total_masc_nao INTEGER,
    total_fem_alf INTEGER,
    total_fem_nao INTEGER
);