# Trabalho Prático
Trabalho prático da disciplina de Introdução da Banco de Dados - DCC011.

## Objetivo

Este projeto monta um pipeline de dados do Censo 2022 para o recorte territorial de Belo Horizonte, a partir de arquivos públicos do IBGE. O fluxo baixa os dados, carrega os arquivos brutos em tabelas de staging, transforma os dados em um modelo relacional e gera arquivos de checagem e consulta.

## Dependências

- Python 3.10 ou superior
- Biblioteca requests
- DuckDB para Python
- DuckDB CLI (opcional para o fluxo via comando, mas recomendado)

## Instalação

No Windows, a instalação pode ser feita com:

```powershell
python -m pip install -r requirements.txt
```

Se o DuckDB CLI não estiver no PATH, instale-o manualmente ou garanta que o executável esteja acessível no terminal.

## Execução

Na raiz do projeto, execute:

```powershell
python run.py
```

O script cria automaticamente as pastas de dados e outputs, tenta baixar os arquivos obrigatórios e monta o banco DuckDB em [database.duckdb](database.duckdb).

## Fases SQL

```text
drop.sql      -> remove objetos antigos
schema.sql    -> cria tabelas finais
staging.sql   -> carrega CSVs brutos
inserts.sql   -> transforma staging em tabelas finais
checks.sql    -> exporta checagens de qualidade
queries.sql   -> exporta resultados das consultas exploratórias
```

## Estrutura do projeto

- [run.py](run.py): orquestra o fluxo completo.
- [sql/schema.sql](sql/schema.sql): define o modelo relacional final.
- [sql/staging.sql](sql/staging.sql): carrega os CSVs em tabelas temporárias.
- [sql/inserts.sql](sql/inserts.sql): preenche as tabelas finais.
- [sql/queries.sql](sql/queries.sql): gera resultados analíticos em CSV.
- [outputs](outputs): armazena os arquivos exportados.

## Recorte territorial

O recorte de Belo Horizonte é feito pela base territorial nacional de setores censitários, usando o município com código 3106200.

## Saídas produzidas

Ao final da execução, o projeto gera:

- um banco DuckDB em [database.duckdb](database.duckdb)
- arquivos de checagem em [outputs/checks](outputs/checks)
- arquivos de consultas em [outputs/queries](outputs/queries)
