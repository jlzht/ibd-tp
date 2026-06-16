# Censo 2022 — Belo Horizonte

## Dependências

- Python 3.10 ou superior.
- Biblioteca `requests`.
- DuckDB CLI.

## Fases SQL

```text
drop.sql      -> remove objetos antigos
schema.sql    -> cria tabelas finais
staging.sql   -> carrega CSVs brutos
inserts.sql   -> transforma staging em tabelas finais
checks.sql    -> exporta checagens de qualidade
queries.sql   -> exporta resultados das consultas exploratórias
```

## Recorte territorial

O recorte de Belo Horizonte é feito pela base territorial nacional de setores censitários:

```sql
WHERE CD_MUN = '3106200'
```
