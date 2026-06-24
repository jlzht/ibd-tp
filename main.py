import duckdb
import os
from config import (
    CAMINHO_BANCO,
    CAMINHO_CSV_GEO,
    CAMINHO_CSV_DEMOGRAFIA,
    CAMINHO_CSV_ALFABETIZACAO,
    CAMINHO_SCHEMA_SQL,
    CODIGO_MUNICIPIO,
)

# função que cria as tabelas do banco de dados
def cria_schema(con):
    with open(CAMINHO_SCHEMA_SQL, "r", encoding="utf-8") as f:
        con.execute(f.read())

# Função para carregar as tabelas Bairros, Regionais e Setores Censitários
def carrega_geo(con):
    con.execute(f"""
        
        -- criação das regionais
        INSERT INTO regional (cd_regional, nm_regional) -- adiciona o nome e código (chave) ibge da regional
        SELECT cd_subdist, FIRST(nm_subdist)  -- nomeia as regionais com base no nm_subdist (IBGE)
        FROM read_csv_auto('{CAMINHO_CSV_GEO}')  -- base da dados IBGE - Setores Censitários de MG
        WHERE cd_mun = '{CODIGO_MUNICIPIO}' AND cd_subdist IS NOT NULL  -- adiciona ao banco de dados apenas setores de BH (filtragem fora do banco de dados)
        GROUP BY cd_subdist  -- agrupamento por um código, apenas uma regional é criada
        ON CONFLICT DO NOTHING;  -- se houver uma regional não fazer nada 

    """)
    con.execute(f"""
                
        -- criação dos bairros (similar ao processo das regionais)
        INSERT INTO bairro (cd_bairro, nm_bairro, cd_regional)
        SELECT cd_bairro, FIRST(nm_bairro), FIRST(cd_subdist) -- o FIRST serve para pegar o primeiro nome para aquele código e para
        FROM read_csv_auto('{CAMINHO_CSV_GEO}')
        WHERE cd_mun = '{CODIGO_MUNICIPIO}' AND cd_bairro IS NOT NULL
        GROUP BY cd_bairro
        ON CONFLICT DO NOTHING;

    """)
    con.execute(f"""
        
        -- criação dos setores (similar ao processo das regionais e dos bairros)
        INSERT INTO setor_censitario (cd_setor, cd_bairro, situacao, area_km2)
        SELECT cd_setor::VARCHAR, cd_bairro, situacao, area_km2  --converte o código para texto
        FROM read_csv_auto('{CAMINHO_CSV_GEO}')
        WHERE cd_mun = '{CODIGO_MUNICIPIO}' AND cd_setor IS NOT NULL AND cd_bairro IS NOT NULL
        -- não utiliza GROUP_BY, pois há apenas um setor por código, não há repetições
        ON CONFLICT DO NOTHING;

    """)

# FUnção para adicionar criar e adicionar indicador de população 
def carrega_pop(con):
    con.execute(f"""
                
        INSERT INTO indicador_populacao (
            
            -- especifica os atibutos do table
            cd_setor,
            pop_total, pop_masc, pop_fem,
            pop_0_4, pop_5_9, pop_10_14,
            pop_15_19, pop_20_24, pop_25_29,
            pop_30_39, pop_40_49, pop_50_59,
            pop_60_69, pop_70_mais
                
        )
        SELECT
            
            -- converter código do setor em texto
            CAST(cd_setor AS VARCHAR),
                
            -- função COALESCE - serve para converter em INT, se falhar coloca 0
            -- utilizado pq o IBGE usa X em alguns campos, travando o db
                
                            -- CODIFICAÇÃO IBGE     -- NOME DO CAMPO DO IBGE
                            -- vXXXXX               
            COALESCE(TRY_CAST(v01006 AS INT), 0),   -- Quantidade de moradores
            COALESCE(TRY_CAST(v01007 AS INT), 0),   -- Sexo masculino
            COALESCE(TRY_CAST(v01008 AS INT), 0),   -- Sexo feminino
            COALESCE(TRY_CAST(v01031 AS INT), 0),   -- 0 a 4 anos
            COALESCE(TRY_CAST(v01032 AS INT), 0),   -- 5 a 9 anos
            COALESCE(TRY_CAST(v01033 AS INT), 0),   -- 10 a 14 anos
            COALESCE(TRY_CAST(v01034 AS INT), 0),   -- 15 a 19 anos
            COALESCE(TRY_CAST(v01035 AS INT), 0),   -- 20 a 24 anos
            COALESCE(TRY_CAST(v01036 AS INT), 0),   -- 25 a 29 anos
            COALESCE(TRY_CAST(v01037 AS INT), 0),   -- 30 a 39 anos
            COALESCE(TRY_CAST(v01038 AS INT), 0),   -- 40 a 49 anos
            COALESCE(TRY_CAST(v01039 AS INT), 0),   -- 50 a 59 anos
            COALESCE(TRY_CAST(v01040 AS INT), 0),   -- 60 a 69 anos
            COALESCE(TRY_CAST(v01041 AS INT), 0)    --  70 anos ou mais

                
        FROM read_csv_auto('{CAMINHO_CSV_DEMOGRAFIA}') -- banco de dados IBGE Demografia - Censo 2022

         --  pega apenas os setores com código de bh, um setor começa com o código da cidade
        WHERE CAST(cd_setor AS VARCHAR) LIKE '{CODIGO_MUNICIPIO}%' 

        -- se o setor já existir, apaga o valor antigo e escreve de novo
        ON CONFLICT (cd_setor) DO UPDATE SET
            pop_total = EXCLUDED.pop_total,
            pop_masc  = EXCLUDED.pop_masc,
            pop_fem   = EXCLUDED.pop_fem,
            pop_0_4   = EXCLUDED.pop_0_4,
            pop_5_9   = EXCLUDED.pop_5_9,
            pop_10_14 = EXCLUDED.pop_10_14,
            pop_15_19 = EXCLUDED.pop_15_19,
            pop_20_24 = EXCLUDED.pop_20_24,
            pop_25_29 = EXCLUDED.pop_25_29,
            pop_30_39 = EXCLUDED.pop_30_39,
            pop_40_49 = EXCLUDED.pop_40_49,
            pop_50_59 = EXCLUDED.pop_50_59,
            pop_60_69 = EXCLUDED.pop_60_69,
            pop_70_mais = EXCLUDED.pop_70_mais;
    """)

# função para carregar indicies de alfabetização
def carrega_alf(con):
    con.execute(f"""

        -- especifica os atibutos do table      
        INSERT INTO indicador_alfabetizacao (
            cd_setor,
            alf_15_29, nao_alf_15_29,
            alf_30_59, nao_alf_30_59,
            alf_60_mais, nao_alf_60_mais,
            total_masc_alf, total_masc_nao,
            total_fem_alf, total_fem_nao
        )
                
        SELECT
            CAST(cd_setor AS VARCHAR),
                
                            -- CODIFICAÇÃO IBGE     -- NOME DO CAMPO DO IBGE
                            -- vXXXXX               -- PESSOAS ALFABETIZADAS
            COALESCE(TRY_CAST(v00852 AS INT), 0),   -- 15 a 29 anos, Morador sabe ler e escrever
            COALESCE(TRY_CAST(v00853 AS INT), 0),   -- 15 a 29 anos, Morador não sabe ler e escrever
            COALESCE(TRY_CAST(v00854 AS INT), 0),   -- 30 a 59 anos, Morador sabe ler e escrever
            COALESCE(TRY_CAST(v00855 AS INT), 0),   -- 30 a 59 anos, Morador não sabe ler e escrever
            COALESCE(TRY_CAST(v00856 AS INT), 0),   -- 60 anos ou mais, Morador sabe ler e escrever
            COALESCE(TRY_CAST(v00857 AS INT), 0),   -- 60 anos ou mais, Morador não sabe ler e escrever
            COALESCE(TRY_CAST(v00912 AS INT), 0),   -- Sexo masculino, 15 anos ou mais, Morador sabe ler e escrever
            COALESCE(TRY_CAST(v00913 AS INT), 0),   -- Sexo masculino, 15 anos ou mais, Morador não sabe ler e escrever
            COALESCE(TRY_CAST(v00914 AS INT), 0),   -- Sexo feminino, 15 anos ou mais, Morador sabe ler e escrever
            COALESCE(TRY_CAST(v00915 AS INT), 0)    -- Sexo feminino, 15 anos ou mais, Morador não sabe ler e escrever

        FROM read_csv_auto('{CAMINHO_CSV_ALFABETIZACAO}')  -- banco de dados IBGE Alfabetização - Censo 2022
        WHERE CAST(cd_setor AS VARCHAR) LIKE '{CODIGO_MUNICIPIO}%' -- similar ao de demografia

        -- se o setor já existir, apaga o valor antigo e escreve de novo
        ON CONFLICT (cd_setor) DO UPDATE SET
            alf_15_29 = EXCLUDED.alf_15_29,
            nao_alf_15_29 = EXCLUDED.nao_alf_15_29,
            alf_30_59 = EXCLUDED.alf_30_59,
            nao_alf_30_59 = EXCLUDED.nao_alf_30_59,
            alf_60_mais = EXCLUDED.alf_60_mais,
            nao_alf_60_mais = EXCLUDED.nao_alf_60_mais,
            total_masc_alf = EXCLUDED.total_masc_alf,
            total_masc_nao = EXCLUDED.total_masc_nao,
            total_fem_alf = EXCLUDED.total_fem_alf,
            total_fem_nao = EXCLUDED.total_fem_nao;
    """)


def main():
    if not os.path.exists(CAMINHO_CSV_GEO):
        return
    if not os.path.exists(CAMINHO_CSV_ALFABETIZACAO):
        return
    if not os.path.exists(CAMINHO_CSV_DEMOGRAFIA):
        return

    con = duckdb.connect(CAMINHO_BANCO)
    try:
        cria_schema(con)
        carrega_geo(con)
        carrega_pop(con)
        carrega_alf(con)
        
    except Exception as e:
        print(f"ERRO")
        raise
    finally:
        con.close()

if __name__ == "__main__":
    main()