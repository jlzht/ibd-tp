-- Belo Horizonte, CD_MUN = 3106200.
INSERT INTO municipio (cd_municipio, nm_municipio, cd_uf, nm_uf)
SELECT
    CAST(CD_MUN AS VARCHAR) AS cd_municipio,
    MIN(CAST(NM_MUN AS VARCHAR)) AS nm_municipio,
    MIN(CAST(CD_UF AS VARCHAR)) AS cd_uf,
    MIN(CAST(NM_UF AS VARCHAR)) AS nm_uf
FROM stg_setores_br
WHERE CAST(CD_MUN AS VARCHAR) = '3106200'
GROUP BY CAST(CD_MUN AS VARCHAR);

INSERT INTO regional (cd_regional, nm_regional, cd_municipio)
SELECT
    COALESCE(NULLIF(CAST(CD_SUBDIST AS VARCHAR), ''), 'SEM_REGIONAL') AS cd_regional,
    COALESCE(MIN(NULLIF(CAST(NM_SUBDIST AS VARCHAR), '')), 'Sem regional informada') AS nm_regional,
    CAST(CD_MUN AS VARCHAR) AS cd_municipio
FROM stg_setores_br
WHERE CAST(CD_MUN AS VARCHAR) = '3106200'
GROUP BY
    COALESCE(NULLIF(CAST(CD_SUBDIST AS VARCHAR), ''), 'SEM_REGIONAL'),
    CAST(CD_MUN AS VARCHAR);

INSERT INTO bairro (id_bairro, cd_bairro, nm_bairro, cd_regional)
SELECT
    COALESCE(NULLIF(CAST(CD_BAIRRO AS VARCHAR), ''), 'SEM_BAIRRO')
        || '|'
        || COALESCE(NULLIF(CAST(CD_SUBDIST AS VARCHAR), ''), 'SEM_REGIONAL') AS id_bairro,
    COALESCE(NULLIF(CAST(CD_BAIRRO AS VARCHAR), ''), 'SEM_BAIRRO') AS cd_bairro,
    COALESCE(MIN(NULLIF(CAST(NM_BAIRRO AS VARCHAR), '')), 'Sem bairro informado') AS nm_bairro,
    COALESCE(NULLIF(CAST(CD_SUBDIST AS VARCHAR), ''), 'SEM_REGIONAL') AS cd_regional
FROM stg_setores_br
WHERE CAST(CD_MUN AS VARCHAR) = '3106200'
GROUP BY
    COALESCE(NULLIF(CAST(CD_BAIRRO AS VARCHAR), ''), 'SEM_BAIRRO'),
    COALESCE(NULLIF(CAST(CD_SUBDIST AS VARCHAR), ''), 'SEM_REGIONAL');

INSERT INTO setor_censitario (cd_setor, id_bairro, situacao, area_km2)
SELECT
    CAST(CD_SETOR AS VARCHAR) AS cd_setor,
    COALESCE(NULLIF(CAST(CD_BAIRRO AS VARCHAR), ''), 'SEM_BAIRRO')
        || '|'
        || COALESCE(NULLIF(CAST(CD_SUBDIST AS VARCHAR), ''), 'SEM_REGIONAL') AS id_bairro,
    MIN(CAST(SITUACAO AS VARCHAR)) AS situacao,
    TRY_CAST(REPLACE(MIN(NULLIF(CAST(AREA_KM2 AS VARCHAR), '')), ',', '.') AS DOUBLE) AS area_km2
FROM stg_setores_br
WHERE CAST(CD_MUN AS VARCHAR) = '3106200'
  AND NULLIF(CAST(CD_SETOR AS VARCHAR), '') IS NOT NULL
GROUP BY
    CAST(CD_SETOR AS VARCHAR),
    COALESCE(NULLIF(CAST(CD_BAIRRO AS VARCHAR), ''), 'SEM_BAIRRO')
        || '|'
        || COALESCE(NULLIF(CAST(CD_SUBDIST AS VARCHAR), ''), 'SEM_REGIONAL');


INSERT INTO indicador_populacao (
    cd_setor,
    pop_total,
    pop_masculina,
    pop_feminina,
    pop_0_4,
    pop_5_9,
    pop_10_14,
    pop_15_19,
    pop_20_24,
    pop_25_29,
    pop_30_39,
    pop_40_49,
    pop_50_59,
    pop_60_69,
    pop_70_mais
)
SELECT
    s.cd_setor,
    TRY_CAST(NULLIF(d.V01006, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01007, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01008, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01031, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01032, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01033, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01034, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01035, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01036, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01037, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01038, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01039, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01040, '') AS BIGINT),
    TRY_CAST(NULLIF(d.V01041, '') AS BIGINT)
FROM stg_demografia d
JOIN setor_censitario s
    ON CAST(d.CD_setor AS VARCHAR) = s.cd_setor;

INSERT INTO indicador_renda (
    cd_setor,
    responsaveis_domicilio,
    moradores_domicilios,
    variancia_moradores,
    renda_media_responsavel,
    variancia_renda_responsavel,
    renda_mediana_responsavel
)
SELECT
    s.cd_setor,
    TRY_CAST(REPLACE(NULLIF(r.V06001, ''), ',', '.') AS DOUBLE),
    TRY_CAST(REPLACE(NULLIF(r.V06002, ''), ',', '.') AS DOUBLE),
    TRY_CAST(REPLACE(NULLIF(r.V06003, ''), ',', '.') AS DOUBLE),
    TRY_CAST(REPLACE(NULLIF(r.V06004, ''), ',', '.') AS DOUBLE),
    TRY_CAST(REPLACE(NULLIF(r.V06005, ''), ',', '.') AS DOUBLE),
    TRY_CAST(REPLACE(NULLIF(r.V06006, ''), ',', '.') AS DOUBLE)
FROM stg_renda_responsavel r
JOIN setor_censitario s
    ON CAST(r.CD_setor AS VARCHAR) = s.cd_setor;

INSERT INTO indicador_saneamento (
    cd_setor,
    domicilios_pp_ocupados,
    agua_rede_geral,
    agua_encanada_interna,
    agua_nao_encanada,
    esgoto_rede_geral,
    lixo_coletado_servico,
    lixo_terreno_baldio
)
SELECT
    s.cd_setor,
    TRY_CAST(NULLIF(d1.V00001, '') AS BIGINT),
    TRY_CAST(NULLIF(d2.V00111, '') AS BIGINT),
    TRY_CAST(NULLIF(d2.V00199, '') AS BIGINT),
    TRY_CAST(NULLIF(d2.V00201, '') AS BIGINT),
    TRY_CAST(NULLIF(d2.V00309, '') AS BIGINT),
    TRY_CAST(NULLIF(d2.V00397, '') AS BIGINT),
    TRY_CAST(NULLIF(d2.V00401, '') AS BIGINT)
FROM stg_domicilio1 d1
JOIN setor_censitario s
    ON CAST(d1.CD_setor AS VARCHAR) = s.cd_setor
LEFT JOIN stg_domicilio2 d2
    ON CAST(d2.setor AS VARCHAR) = s.cd_setor;

INSERT INTO indicador_alfabetizacao (
    cd_setor,
    alf_15mais_sabe_ler,
    alf_15mais_nao_sabe_ler,
    alf_15_29_sabe_ler,
    alf_15_29_nao_sabe_ler,
    alf_30_59_sabe_ler,
    alf_30_59_nao_sabe_ler,
    alf_60mais_sabe_ler,
    alf_60mais_nao_sabe_ler
)
SELECT
    s.cd_setor,
    TRY_CAST(NULLIF(a.V00900, '') AS BIGINT),
    TRY_CAST(NULLIF(a.V00901, '') AS BIGINT),
    TRY_CAST(NULLIF(a.V00852, '') AS BIGINT),
    TRY_CAST(NULLIF(a.V00853, '') AS BIGINT),
    TRY_CAST(NULLIF(a.V00854, '') AS BIGINT),
    TRY_CAST(NULLIF(a.V00855, '') AS BIGINT),
    TRY_CAST(NULLIF(a.V00856, '') AS BIGINT),
    TRY_CAST(NULLIF(a.V00857, '') AS BIGINT)
FROM stg_alfabetizacao a
JOIN setor_censitario s
    ON CAST(a.CD_setor AS VARCHAR) = s.cd_setor;
