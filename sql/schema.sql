CREATE TABLE municipio (
    cd_municipio VARCHAR PRIMARY KEY,
    nm_municipio VARCHAR NOT NULL,
    cd_uf VARCHAR NOT NULL,
    nm_uf VARCHAR NOT NULL
);

CREATE TABLE regional (
    cd_regional VARCHAR PRIMARY KEY,
    nm_regional VARCHAR NOT NULL,
    cd_municipio VARCHAR NOT NULL,
    FOREIGN KEY (cd_municipio) REFERENCES municipio(cd_municipio)
);

CREATE TABLE bairro (
    id_bairro VARCHAR PRIMARY KEY,
    cd_bairro VARCHAR,
    nm_bairro VARCHAR NOT NULL,
    cd_regional VARCHAR NOT NULL,
    FOREIGN KEY (cd_regional) REFERENCES regional(cd_regional)
);

CREATE TABLE setor_censitario (
    cd_setor VARCHAR PRIMARY KEY,
    id_bairro VARCHAR NOT NULL,
    situacao VARCHAR,
    area_km2 DOUBLE,
    FOREIGN KEY (id_bairro) REFERENCES bairro(id_bairro),
    CHECK (area_km2 IS NULL OR area_km2 >= 0)
);

CREATE TABLE indicador_populacao (
    cd_setor VARCHAR PRIMARY KEY,
    pop_total BIGINT,
    pop_masculina BIGINT,
    pop_feminina BIGINT,
    pop_0_4 BIGINT,
    pop_5_9 BIGINT,
    pop_10_14 BIGINT,
    pop_15_19 BIGINT,
    pop_20_24 BIGINT,
    pop_25_29 BIGINT,
    pop_30_39 BIGINT,
    pop_40_49 BIGINT,
    pop_50_59 BIGINT,
    pop_60_69 BIGINT,
    pop_70_mais BIGINT,
    FOREIGN KEY (cd_setor) REFERENCES setor_censitario(cd_setor)
);

CREATE TABLE indicador_renda (
    cd_setor VARCHAR PRIMARY KEY,
    responsaveis_domicilio DOUBLE,
    moradores_domicilios DOUBLE,
    variancia_moradores DOUBLE,
    renda_media_responsavel DOUBLE,
    variancia_renda_responsavel DOUBLE,
    renda_mediana_responsavel DOUBLE,
    FOREIGN KEY (cd_setor) REFERENCES setor_censitario(cd_setor)
);

CREATE TABLE indicador_saneamento (
    cd_setor VARCHAR PRIMARY KEY,
    domicilios_pp_ocupados BIGINT,
    agua_rede_geral BIGINT,
    agua_encanada_interna BIGINT,
    agua_nao_encanada BIGINT,
    esgoto_rede_geral BIGINT,
    lixo_coletado_servico BIGINT,
    lixo_terreno_baldio BIGINT,
    FOREIGN KEY (cd_setor) REFERENCES setor_censitario(cd_setor)
);

CREATE TABLE indicador_alfabetizacao (
    cd_setor VARCHAR PRIMARY KEY,
    alf_15mais_sabe_ler BIGINT,
    alf_15mais_nao_sabe_ler BIGINT,
    alf_15_29_sabe_ler BIGINT,
    alf_15_29_nao_sabe_ler BIGINT,
    alf_30_59_sabe_ler BIGINT,
    alf_30_59_nao_sabe_ler BIGINT,
    alf_60mais_sabe_ler BIGINT,
    alf_60mais_nao_sabe_ler BIGINT,
    FOREIGN KEY (cd_setor) REFERENCES setor_censitario(cd_setor)
);
