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
