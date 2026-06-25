COPY (
    SELECT 'municipio' AS tabela, COUNT(*) AS registros FROM municipio
    UNION ALL SELECT 'regional', COUNT(*) FROM regional
    UNION ALL SELECT 'bairro', COUNT(*) FROM bairro
    UNION ALL SELECT 'setor_censitario', COUNT(*) FROM setor_censitario
    UNION ALL SELECT 'indicador_populacao', COUNT(*) FROM indicador_populacao
    UNION ALL SELECT 'indicador_renda', COUNT(*) FROM indicador_renda
    UNION ALL SELECT 'indicador_saneamento', COUNT(*) FROM indicador_saneamento
    UNION ALL SELECT 'indicador_alfabetizacao', COUNT(*) FROM indicador_alfabetizacao
)
TO 'outputs/checks/contagem_tabelas.csv'
WITH (HEADER, DELIMITER ',');

COPY (
    SELECT 'stg_setores_br' AS tabela, COUNT(*) AS registros FROM stg_setores_br
    UNION ALL SELECT 'stg_demografia', COUNT(*) FROM stg_demografia
    UNION ALL SELECT 'stg_domicilio1', COUNT(*) FROM stg_domicilio1
    UNION ALL SELECT 'stg_domicilio2', COUNT(*) FROM stg_domicilio2
    UNION ALL SELECT 'stg_domicilio3', COUNT(*) FROM stg_domicilio3
    UNION ALL SELECT 'stg_renda_responsavel', COUNT(*) FROM stg_renda_responsavel
    UNION ALL SELECT 'stg_alfabetizacao', COUNT(*) FROM stg_alfabetizacao
)
TO 'outputs/checks/contagem_staging.csv'
WITH (HEADER, DELIMITER ',');

COPY (
    SELECT 'municipio' AS tabela, 'cd_municipio' AS coluna, COUNT(*) AS total_registros,
           COUNT(*) FILTER (WHERE cd_municipio IS NULL OR TRIM(cd_municipio) = '') AS valores_nulos,
           COUNT(*) - COUNT(DISTINCT cd_municipio) AS valores_duplicados
    FROM municipio
    UNION ALL
    SELECT 'regional', 'cd_regional', COUNT(*),
           COUNT(*) FILTER (WHERE cd_regional IS NULL OR TRIM(cd_regional) = ''),
           COUNT(*) - COUNT(DISTINCT cd_regional)
    FROM regional
    UNION ALL
    SELECT 'bairro', 'id_bairro', COUNT(*),
           COUNT(*) FILTER (WHERE id_bairro IS NULL OR TRIM(id_bairro) = ''),
           COUNT(*) - COUNT(DISTINCT id_bairro)
    FROM bairro
    UNION ALL
    SELECT 'setor_censitario', 'cd_setor', COUNT(*),
           COUNT(*) FILTER (WHERE cd_setor IS NULL OR TRIM(cd_setor) = ''),
           COUNT(*) - COUNT(DISTINCT cd_setor)
    FROM setor_censitario
    UNION ALL
    SELECT 'indicador_populacao', 'cd_setor', COUNT(*),
           COUNT(*) FILTER (WHERE cd_setor IS NULL OR TRIM(cd_setor) = ''),
           COUNT(*) - COUNT(DISTINCT cd_setor)
    FROM indicador_populacao
    UNION ALL
    SELECT 'indicador_renda', 'cd_setor', COUNT(*),
           COUNT(*) FILTER (WHERE cd_setor IS NULL OR TRIM(cd_setor) = ''),
           COUNT(*) - COUNT(DISTINCT cd_setor)
    FROM indicador_renda
    UNION ALL
    SELECT 'indicador_saneamento', 'cd_setor', COUNT(*),
           COUNT(*) FILTER (WHERE cd_setor IS NULL OR TRIM(cd_setor) = ''),
           COUNT(*) - COUNT(DISTINCT cd_setor)
    FROM indicador_saneamento
    UNION ALL
    SELECT 'indicador_alfabetizacao', 'cd_setor', COUNT(*),
           COUNT(*) FILTER (WHERE cd_setor IS NULL OR TRIM(cd_setor) = ''),
           COUNT(*) - COUNT(DISTINCT cd_setor)
    FROM indicador_alfabetizacao
)
TO 'outputs/checks/qualidade_dados.csv'
WITH (HEADER, DELIMITER ',');

COPY (
    SELECT
        s.cd_setor,
        b.nm_bairro,
        r.nm_regional,
        'indicador_populacao' AS indicador_sem_dados
    FROM setor_censitario s
    JOIN bairro b
        ON s.id_bairro = b.id_bairro
    JOIN regional r
        ON b.cd_regional = r.cd_regional
    LEFT JOIN indicador_populacao p
        ON s.cd_setor = p.cd_setor
    WHERE p.cd_setor IS NULL

    UNION ALL

    SELECT
        s.cd_setor,
        b.nm_bairro,
        r.nm_regional,
        'indicador_renda' AS indicador_sem_dados
    FROM setor_censitario s
    JOIN bairro b
        ON s.id_bairro = b.id_bairro
    JOIN regional r
        ON b.cd_regional = r.cd_regional
    LEFT JOIN indicador_renda renda
        ON s.cd_setor = renda.cd_setor
    WHERE renda.cd_setor IS NULL

    UNION ALL

    SELECT
        s.cd_setor,
        b.nm_bairro,
        r.nm_regional,
        'indicador_saneamento' AS indicador_sem_dados
    FROM setor_censitario s
    JOIN bairro b
        ON s.id_bairro = b.id_bairro
    JOIN regional r
        ON b.cd_regional = r.cd_regional
    LEFT JOIN indicador_saneamento san
        ON s.cd_setor = san.cd_setor
    WHERE san.cd_setor IS NULL

    UNION ALL

    SELECT
        s.cd_setor,
        b.nm_bairro,
        r.nm_regional,
        'indicador_alfabetizacao' AS indicador_sem_dados
    FROM setor_censitario s
    JOIN bairro b
        ON s.id_bairro = b.id_bairro
    JOIN regional r
        ON b.cd_regional = r.cd_regional
    LEFT JOIN indicador_alfabetizacao alf
        ON s.cd_setor = alf.cd_setor
    WHERE alf.cd_setor IS NULL
)
TO 'outputs/checks/setores_sem_dados.csv'
WITH (HEADER, DELIMITER ',');
