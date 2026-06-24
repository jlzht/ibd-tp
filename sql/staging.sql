CREATE OR REPLACE TABLE stg_setores_br AS
SELECT *
FROM read_csv_auto('data/raw/BR_setores_CD2022.csv', header = true, all_varchar = true);

CREATE OR REPLACE TABLE stg_demografia AS
SELECT *
FROM read_csv_auto('data/raw/Agregados_por_setores_demografia_BR.csv', header = true, all_varchar = true);

CREATE OR REPLACE TABLE stg_domicilio1 AS
SELECT *
FROM read_csv_auto('data/raw/Agregados_por_setores_caracteristicas_domicilio1_BR.csv', header = true, all_varchar = true);

CREATE OR REPLACE TABLE stg_domicilio2 AS
SELECT *
FROM read_csv_auto('data/raw/Agregados_por_setores_caracteristicas_domicilio2_BR.csv', header = true, all_varchar = true);

CREATE OR REPLACE TABLE stg_domicilio3 AS
SELECT *
FROM read_csv_auto('data/raw/Agregados_por_setores_caracteristicas_domicilio3_BR.csv', header = true, all_varchar = true);

CREATE OR REPLACE TABLE stg_renda_responsavel AS
SELECT *
FROM read_csv_auto('data/raw/Agregados_por_setores_renda_responsavel_BR.csv', header = true, all_varchar = true);

CREATE OR REPLACE TABLE stg_alfabetizacao AS
SELECT *
FROM read_csv_auto('data/raw/Agregados_por_setores_alfabetizacao_BR.csv', header = true, all_varchar = true);
