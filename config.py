import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAMINHO_BANCO = os.path.join(BASE_DIR, 'bh_censo.duckdb')
CAMINHO_CSV_GEO = os.path.join(BASE_DIR, 'setores_MG.csv')
CAMINHO_CSV_DEMOGRAFIA = os.path.join(BASE_DIR, 'Agregados_por_setores_demografia_BR.csv') # dados de demografia
CAMINHO_SCHEMA_SQL = os.path.join(BASE_DIR, 'schema.sql')

# código IBGE para Belo Horizonte
CODIGO_MUNICIPIO = '3106200'