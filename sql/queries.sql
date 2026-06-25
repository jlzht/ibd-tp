COPY (
    SELECT
        r.nm_regional,
        COUNT(DISTINCT b.id_bairro) AS qtd_bairros,
        COUNT(DISTINCT s.cd_setor) AS qtd_setores,
        SUM(p.pop_total) AS pop_total,
        SUM(s.area_km2) AS area_km2_total,
        SUM(p.pop_total) * 1.0 / NULLIF(SUM(s.area_km2), 0) AS densidade_demografica
    FROM setor_censitario s
    JOIN bairro b
        ON s.id_bairro = b.id_bairro
    JOIN regional r
        ON b.cd_regional = r.cd_regional
    LEFT JOIN indicador_populacao p
        ON s.cd_setor = p.cd_setor
    GROUP BY
        r.nm_regional
    ORDER BY
        pop_total DESC
)
TO 'outputs/queries/populacao_por_regional.csv'
WITH (HEADER, DELIMITER ',');

COPY (
    SELECT
        r.nm_regional,
        b.nm_bairro,
        COUNT(DISTINCT s.cd_setor) AS qtd_setores,
        SUM(p.pop_total) AS pop_total,
        ROUND(SUM(s.area_km2), 4) AS area_km2_total,
        ROUND(
            SUM(p.pop_total) * 1.0 / NULLIF(SUM(s.area_km2), 0),
            2
        ) AS densidade_demografica
    FROM setor_censitario s
    JOIN bairro b
        ON s.id_bairro = b.id_bairro
    JOIN regional r
        ON b.cd_regional = r.cd_regional
    LEFT JOIN indicador_populacao p
        ON s.cd_setor = p.cd_setor
    GROUP BY
        r.nm_regional,
        b.nm_bairro
    HAVING
        SUM(s.area_km2) > 0
        AND SUM(p.pop_total) IS NOT NULL
    ORDER BY
        densidade_demografica DESC
    LIMIT 10
)
TO 'outputs/queries/bairros_maior_densidade.csv'
WITH (HEADER, DELIMITER ',');

-- Desigualdade de renda por bairro
COPY (
    WITH renda_bairro AS (
        SELECT 
            b.cd_regional,
            b.nm_bairro,

            -- média ponderada da renda de um setor, evita discrepancias 
            SUM(ir.renda_media_responsavel * ir.responsaveis_domicilio) 
                / NULLIF(SUM(ir.responsaveis_domicilio), 0) AS renda_media_ponderada,
                
            -- mediana da mediana do bairro
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ir.renda_mediana_responsavel) AS renda_mediana_bairro
        
        FROM indicador_renda ir
        JOIN setor_censitario s ON ir.cd_setor = s.cd_setor
        JOIN bairro b ON s.id_bairro = b.id_bairro

        WHERE ir.responsaveis_domicilio > 0 
          AND ir.renda_media_responsavel > 0
          AND ir.renda_mediana_responsavel > 0 -- sem setores sem renda (pessoas)
        GROUP BY b.cd_regional, b.nm_bairro
    )
    SELECT 
        -- exportar para um csv que será analisado no QGIS
        r.nm_regional,
        rb.nm_bairro,
        rb.renda_media_ponderada,
        rb.renda_mediana_bairro,

        -- cálculo média/mediana que resulta em um indicador de desigualdade no bairro
        -- médias altas com medianas baixa indica que há bastante desigualdade no bairro
        
        (rb.renda_media_ponderada / NULLIF(rb.renda_mediana_bairro, 0)) AS razao_media_mediana
    FROM renda_bairro rb
    JOIN regional r ON rb.cd_regional = r.cd_regional
    ORDER BY razao_media_mediana DESC

) TO 'outputs/queries/desigualdade_bairros.csv' (HEADER, DELIMITER ',');

-- Relação entre saneamento e renda
COPY (
    WITH saneamento_bairro AS (
        SELECT 
            b.cd_regional,
            b.nm_bairro,
            
            -- soma de todos os domicilios ocupados
            SUM(i.domicilios_pp_ocupados) AS total_domicilios,

            -- cálculo do percentual de esgoto, arredondamento em 4 casas decimais, por bairro
            ROUND(SUM(i.esgoto_rede_geral) * 1.0 / NULLIF(SUM(i.domicilios_pp_ocupados), 0), 4) AS perc_esgoto,
            
            -- cálculo média da renda ponderada
            ROUND(SUM(ir.renda_media_responsavel * ir.responsaveis_domicilio) 
                / NULLIF(SUM(ir.responsaveis_domicilio), 0), 2) AS renda_media_bairro

        FROM indicador_saneamento i
        JOIN indicador_renda ir ON i.cd_setor = ir.cd_setor
        JOIN setor_censitario s ON i.cd_setor = s.cd_setor
        JOIN bairro b ON s.id_bairro = b.id_bairro
        WHERE i.domicilios_pp_ocupados > 0
          AND ir.responsaveis_domicilio > 0
        GROUP BY b.cd_regional, b.nm_bairro
        HAVING SUM(i.domicilios_pp_ocupados) >= 30 -- filtro para evitar bairros com poucos domicilios
    )
    SELECT 
        r.nm_regional,
        sb.nm_bairro,
        (sb.perc_esgoto * 100) AS perc_esgoto,
        sb.renda_media_bairro

    FROM saneamento_bairro sb
    JOIN regional r ON sb.cd_regional = r.cd_regional
    ORDER BY sb.perc_esgoto ASC -- ordenação crescente
) TO 'outputs/queries/saneamento_renda.csv' (HEADER, DELIMITER ',');

COPY (
    WITH base_bairro AS (
        SELECT 
            b.cd_regional,
            b.nm_bairro,
            -- renda média do bairro
            SUM(ir.renda_media_responsavel * ir.responsaveis_domicilio) 
                / NULLIF(SUM(ir.responsaveis_domicilio), 0) AS renda_media,

            -- percentual com esgoto
            SUM(i.esgoto_rede_geral) * 1.0 
                / NULLIF(SUM(i.domicilios_pp_ocupados), 0) AS perc_esgoto,

            -- taxa de analfabetismo
            SUM(ia.alf_15mais_nao_sabe_ler) * 1.0 
                / NULLIF(SUM(ia.alf_15mais_sabe_ler + ia.alf_15mais_nao_sabe_ler), 0) AS taxa_analf
        
        FROM bairro b
        JOIN setor_censitario s ON b.id_bairro = s.id_bairro
        JOIN indicador_renda ir ON s.cd_setor = ir.cd_setor
        JOIN indicador_saneamento i ON s.cd_setor = i.cd_setor
        JOIN indicador_alfabetizacao ia ON s.cd_setor = ia.cd_setor
        WHERE ir.responsaveis_domicilio > 0 
          AND i.domicilios_pp_ocupados > 0
        GROUP BY b.cd_regional, b.nm_bairro
        HAVING SUM(i.domicilios_pp_ocupados) >= 20 -- amostra mínima
    ),

    estatisticas_globais AS (
        -- médias e desvios padrão de BH para cada indicador
        SELECT 
            AVG(renda_media) AS media_renda, 
            STDDEV(renda_media) AS std_renda,
            AVG(perc_esgoto) AS media_esgoto, 
            STDDEV(perc_esgoto) AS std_esgoto,
            AVG(taxa_analf) AS media_analf, 
            STDDEV(taxa_analf) AS std_analf
        FROM base_bairro
    )

    -- consulta final 
    SELECT 
        r.nm_regional,
        bb.nm_bairro,
        ROUND(bb.renda_media, 2) AS renda_media,
        ROUND(bb.perc_esgoto * 100, 2) AS perc_esgoto,
        ROUND(bb.taxa_analf * 100, 2) AS perc_analfabetismo,

        -- índice de vulnerabilidade 
        ROUND(
            ((eg.media_renda - bb.renda_media) / eg.std_renda) +
            ((eg.media_esgoto - bb.perc_esgoto) / eg.std_esgoto) +
            ((bb.taxa_analf - eg.media_analf) / eg.std_analf)
        , 2) AS indice_vulnerabilidade

    FROM base_bairro bb
    CROSS JOIN estatisticas_globais eg
    JOIN regional r ON bb.cd_regional = r.cd_regional
    ORDER BY indice_vulnerabilidade DESC -- do mais vulnerável para o menos

) TO 'outputs/queries/vulnerabilidade.csv' (HEADER, DELIMITER ',');
