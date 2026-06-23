import duckdb
import os
from config import (
    CAMINHO_BANCO,
    CAMINHO_CSV_GEO,
    CAMINHO_CSV_DEMOGRAFIA,
    CAMINHO_SCHEMA_SQL,
    CODIGO_MUNICIPIO,
)

def cria_schema(con):
    with open(CAMINHO_SCHEMA_SQL, "r", encoding="utf-8") as f:
        con.execute(f.read())

# Função para carregar as tabelas Bairros, Regionais e Setores Censitários
def carrega_geo(con):
    con.execute(f"""
        INSERT INTO regional (cd_regional, nm_regional)
        SELECT cd_subdist, FIRST(nm_subdist)
        FROM read_csv_auto('{CAMINHO_CSV_GEO}')
        WHERE cd_mun = '{CODIGO_MUNICIPIO}' AND cd_subdist IS NOT NULL 
        GROUP BY cd_subdist
        ON CONFLICT DO NOTHING;
    """)
    con.execute(f"""
        INSERT INTO bairro (cd_bairro, nm_bairro, cd_regional)
        SELECT cd_bairro, FIRST(nm_bairro), FIRST(cd_subdist)
        FROM read_csv_auto('{CAMINHO_CSV_GEO}')
        WHERE cd_mun = '{CODIGO_MUNICIPIO}' AND cd_bairro IS NOT NULL
        GROUP BY cd_bairro
        ON CONFLICT DO NOTHING;
    """)
    con.execute(f"""
        INSERT INTO setor_censitario (cd_setor, cd_bairro, situacao, area_km2)
        SELECT cd_setor::VARCHAR, cd_bairro, situacao, area_km2
        FROM read_csv_auto('{CAMINHO_CSV_GEO}')
        WHERE cd_mun = '{CODIGO_MUNICIPIO}' AND cd_setor IS NOT NULL AND cd_bairro IS NOT NULL
        ON CONFLICT DO NOTHING;
    """)

# FUnção para adicionar criar e adicionar indicador de população 
def carrega_pop(con):
    con.execute(f"""
        INSERT INTO indicador_populacao (cd_setor, pop_total, pop_masc, pop_fem)
        SELECT
            CAST(cd_setor AS VARCHAR),
            COALESCE(TRY_CAST(v01006 AS INT), 0), -- Quantidade de moradores 
            COALESCE(TRY_CAST(v01007 AS INT), 0), -- Sexo masculino
            COALESCE(TRY_CAST(v01008 AS INT), 0)  -- Sexo feminino
        FROM read_csv_auto('{CAMINHO_CSV_DEMOGRAFIA}')
        WHERE CAST(cd_setor AS VARCHAR) LIKE '{CODIGO_MUNICIPIO}%'
        ON CONFLICT (cd_setor) DO UPDATE SET
            pop_total = EXCLUDED.pop_total,
            pop_masc  = EXCLUDED.pop_masc,
            pop_fem   = EXCLUDED.pop_fem;   -- comandos de atualização EXCLUDED
    """)
    sem_pop = con.execute("""
        SELECT COUNT(*)
        FROM setor_censitario s
        LEFT JOIN indicador_populacao p ON s.cd_setor = p.cd_setor
        WHERE p.cd_setor IS NULL
    """).fetchone()[0]
    if sem_pop:
        print(F"{sem_pop} - SEM POPULAÇÃO")
    else:
        print("TODOS OS SETORES TEM POPULAÇÃO")

def main():
    if not os.path.exists(CAMINHO_CSV_GEO):
        return
    if not os.path.exists(CAMINHO_CSV_DEMOGRAFIA):
        return

    con = duckdb.connect(CAMINHO_BANCO)
    try:
        cria_schema(con)
        carrega_geo(con)
        carrega_pop(con)
    except Exception as e:
        print(f"ERRO")
        raise
    finally:
        con.close()

if __name__ == "__main__":
    main()