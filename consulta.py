import duckdb
import pandas as pd
from config import CAMINHO_BANCO

def consultar():
    
    # conexão com o banco de dados
    con = duckdb.connect(CAMINHO_BANCO, read_only=True)

    # consulta para cada regional de belo horizonte
    query_regional = """

    -- modo de consulta temporário
    WITH pop_alf_reg AS (
        SELECT 

            r.nm_regional,
            SUM(p.pop_total - p.pop_0_4 - p.pop_5_9 - p.pop_10_14) AS pop_15_mais, -- separação para população total menor de de 15 anos, da tabela de indicador de população por setor
            SUM(a.alf_15_29 + a.alf_30_59 + a.alf_60_mais) AS alfabetizados   -- total de pessoas alfabetizadas por setor
        
        FROM setor_censitario s
        JOIN bairro b ON s.cd_bairro = b.cd_bairro  -- união para saber a qual bairro cada setor está 
        JOIN regional r ON b.cd_regional = r.cd_regional  -- união para saber a qual regional cada setor está  
        JOIN indicador_populacao p ON s.cd_setor = p.cd_setor  -- união para trazer os dados populacionas para setor
        JOIN indicador_alfabetizacao a ON s.cd_setor = a.cd_setor -- união com setores para incluir os dados populacionais em indicador_alfabetização
        
        GROUP BY r.nm_regional -- agrupamento dos setores por nome da regional que pertence
    )
    SELECT 

        nm_regional,
        pop_15_mais,
        alfabetizados,

        -- calculo da taxa de alfabetizados, com arredondamento
        ROUND(100.0 * alfabetizados / pop_15_mais, 2) AS taxa  

    FROM pop_alf_reg
    ORDER BY taxa DESC  -- ordenação por regionais com menores taxas de pessoas alfabetizadas
    """

    # consulta para nome de bairro
    query_bairro = """
    
    -- modo de consulta temporário
    WITH pop_alf_bairro AS (
        SELECT 

            b.nm_bairro,
            SUM(p.pop_total - p.pop_0_4 - p.pop_5_9 - p.pop_10_14) AS pop_15_mais, -- mesmo processo da regional
            SUM(a.alf_15_29 + a.alf_30_59 + a.alf_60_mais) AS alfabetizados

        FROM setor_censitario s

        JOIN bairro b ON s.cd_bairro = b.cd_bairro  -- mesmo processo regional, pórem simplificado por não usar as regionais
        JOIN indicador_populacao p ON s.cd_setor = p.cd_setor
        JOIN indicador_alfabetizacao a ON s.cd_setor = a.cd_setor
        GROUP BY b.nm_bairro
    )
    SELECT 

        nm_bairro,
        pop_15_mais,
        alfabetizados,

        -- calculo da taxa de alfabetizados, com arredondamento
        ROUND(100.0 * alfabetizados / pop_15_mais, 2) AS taxa

    FROM pop_alf_bairro
    WHERE pop_15_mais > 0
    ORDER BY taxa DESC -- ordenação por bairros com menores taxas de pessoas alfabetizadas
    """

    query = """
    SELECT
        SUM(total_masc_alf) AS homens_alf,
        SUM(total_fem_alf) AS mulheres_alf
    FROM indicador_alfabetizacao
    """

    # resultados da consulta por regional
    print("taxa de alfabetização por regional de BH")
    df_reg = con.execute(query_regional).df()
    print(df_reg.to_string(index=False))

    print("taxa de alfabetização por bairro de BH")
    df_bairro = con.execute(query_bairro).df()
    print(df_bairro.to_string(index=False))

    con.close()

if __name__ == "__main__":
    consultar()