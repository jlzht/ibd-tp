import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import requests

PROJECT_ROOT = Path(__file__).resolve().parent

DB_PATH = PROJECT_ROOT / "database.duckdb"

DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_ZIP_DIR = PROJECT_ROOT / "data" / "zip"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

SQL_PHASES = [
    PROJECT_ROOT / "sql" / "drop.sql",
    PROJECT_ROOT / "sql" / "schema.sql",
    PROJECT_ROOT / "sql" / "staging.sql",
    PROJECT_ROOT / "sql" / "inserts.sql",
    PROJECT_ROOT / "sql" / "checks.sql",
    PROJECT_ROOT / "sql" / "queries.sql",
]


REQUIRED_FILES = {
    "BR_setores_CD2022.csv": {
        "url": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/malha_com_atributos/setores/csv/BR_setores_CD2022.csv",
        "description": "Malha com atributos dos setores censitários do Brasil",
        "kind": "csv",
    },
    "Agregados_por_setores_demografia_BR.csv": {
        "url": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_demografia_BR.zip",
        "description": "Agregados por setores - Demografia",
        "kind": "csv_zip",
    },
    "Agregados_por_setores_caracteristicas_domicilio1_BR.csv": {
        "url": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_caracteristicas_domicilio1_BR.zip",
        "description": "Agregados por setores - Características do Domicílio - Parte 1",
        "kind": "csv_zip",
    },
    "Agregados_por_setores_caracteristicas_domicilio2_BR.csv": {
        "url": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_caracteristicas_domicilio2_BR_20250417.zip",
        "description": "Agregados por setores - Características do Domicílio - Parte 2",
        "kind": "csv_zip",
    },
    "Agregados_por_setores_caracteristicas_domicilio3_BR.csv": {
        "url": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_caracteristicas_domicilio3_BR_20250417.zip",
        "description": "Agregados por setores - Características do Domicílio - Parte 3",
        "kind": "csv_zip",
    },
    "Agregados_por_setores_renda_responsavel_BR.csv": {
        "url": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/Agregados_por_setores_renda_responsavel_BR_20260508_csv.zip",
        "description": "Agregados por setores - Renda do responsável",
        "kind": "csv_zip",
    },
    "Agregados_por_setores_alfabetizacao_BR.csv": {
        "url": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_alfabetizacao_BR.zip",
        "description": "Agregados por setores - Alfabetização",
        "kind": "csv_zip",
    },
}


def ensure_directories() -> None:
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_ZIP_DIR.mkdir(parents=True, exist_ok=True)

    (OUTPUTS_DIR / "checks").mkdir(parents=True, exist_ok=True)
    (OUTPUTS_DIR / "queries").mkdir(parents=True, exist_ok=True)


def required_file_exists(filename: str) -> bool:
    return (DATA_RAW_DIR / filename).exists()


def download_file(url: str, destination: Path) -> None:
    print(f"Baixando: {url}")
    print(f"Destino: {destination}")

    try:
        with requests.get(url, stream=True, timeout=120) as response:
            response.raise_for_status()

            with destination.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)

    except requests.RequestException as exc:
        if destination.exists():
            destination.unlink()

        raise RuntimeError(f"Erro ao baixar {url}: {exc}") from exc


def find_expected_csv(extract_dir: Path, expected_filename: str) -> Path:
    csv_files = list(extract_dir.rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"Nenhum CSV encontrado dentro do ZIP para {expected_filename}."
        )

    for csv_file in csv_files:
        if csv_file.name == expected_filename:
            return csv_file

    for csv_file in csv_files:
        if csv_file.name.lower() == expected_filename.lower():
            return csv_file

    expected_stem = Path(expected_filename).stem.lower()

    for csv_file in csv_files:
        if csv_file.stem.lower() == expected_stem:
            return csv_file

    for csv_file in csv_files:
        normalized_actual = re.sub(r"_\d{8}$", "", csv_file.stem.lower())
        if normalized_actual == expected_stem:
            return csv_file

    found_files = "\n".join(
        f"- {csv_file.relative_to(extract_dir)}" for csv_file in csv_files
    )

    raise FileNotFoundError(
        f"CSV esperado não encontrado dentro do ZIP: {expected_filename}\n"
        f"CSVs encontrados:\n{found_files}"
    )


def extract_expected_csv(zip_path: Path, expected_filename: str) -> None:
    extract_dir = DATA_ZIP_DIR / f"extract_{zip_path.stem}"

    if extract_dir.exists():
        shutil.rmtree(extract_dir)

    extract_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        source_csv = find_expected_csv(extract_dir, expected_filename)
        destination_csv = DATA_RAW_DIR / expected_filename

        shutil.copyfile(source_csv, destination_csv)

        print(f"Extraído: {destination_csv}")

    finally:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)


def download_required_file(filename: str, metadata: dict) -> None:
    url = metadata["url"]
    kind = metadata["kind"]

    if kind == "csv":
        destination = DATA_RAW_DIR / filename
        download_file(url, destination)
        return

    if kind == "csv_zip":
        zip_path = DATA_ZIP_DIR / f"{Path(filename).stem}.zip"

        download_file(url, zip_path)
        extract_expected_csv(zip_path, filename)
        return

    raise ValueError(f"Tipo de arquivo não suportado para {filename}: {kind}")


def ensure_required_csvs() -> None:
    missing_files = [
        filename
        for filename in REQUIRED_FILES
        if not required_file_exists(filename)
    ]

    if not missing_files:
        print("Todos os CSVs obrigatórios já existem em data/raw/.")
        return

    print("Alguns CSVs obrigatórios não foram encontrados.")
    print()

    for filename in missing_files:
        print(f"- {filename}: {REQUIRED_FILES[filename]['description']}")

    print()
    print("Tentando baixar os arquivos ausentes...")
    print()

    errors = []

    for filename in missing_files:
        try:
            download_required_file(filename, REQUIRED_FILES[filename])
        except Exception as exc:
            errors.append((filename, exc))

    if errors:
        print()
        print("Não foi possível obter todos os CSVs automaticamente.")
        print("Arquivos com erro:")

        for filename, exc in errors:
            print(f"- {filename}: {exc}")

        print()
        print("Coloque manualmente os arquivos abaixo em data/raw/ ou corrija as URLs:")
        for filename in REQUIRED_FILES:
            print(f"  - data/raw/{filename}")

        sys.exit(1)

    print()
    print("Todos os CSVs foram obtidos com sucesso.")


def ensure_duckdb_available() -> None:
    if shutil.which("duckdb") is None:
        raise RuntimeError(
            "DuckDB CLI não encontrado. Instale o DuckDB e garanta que o comando "
            "'duckdb' esteja disponível no PATH."
        )


def split_sql_statements(sql_content: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_single_quote = False
    in_double_quote = False
    in_line_comment = False
    in_block_comment = False
    index = 0

    while index < len(sql_content):
        char = sql_content[index]
        next_char = sql_content[index + 1] if index + 1 < len(sql_content) else ""

        if in_line_comment:
            current.append(char)
            if char == "\n":
                in_line_comment = False
            index += 1
            continue

        if in_block_comment:
            current.append(char)
            if char == "*" and next_char == "/":
                current.append(next_char)
                in_block_comment = False
                index += 2
                continue
            index += 1
            continue

        if in_single_quote:
            current.append(char)
            if char == "'":
                in_single_quote = False
            index += 1
            continue

        if in_double_quote:
            current.append(char)
            if char == '"':
                in_double_quote = False
            index += 1
            continue

        if char == "-" and next_char == "-":
            current.append("--")
            in_line_comment = True
            index += 2
            continue

        if char == "/" and next_char == "*":
            current.append("/*")
            in_block_comment = True
            index += 2
            continue

        if char == "'":
            current.append(char)
            in_single_quote = True
            index += 1
            continue

        if char == '"':
            current.append(char)
            in_double_quote = True
            index += 1
            continue

        if char == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            index += 1
            continue

        current.append(char)
        index += 1

    tail = "".join(current).strip()
    if tail:
        statements.append(tail)

    return statements


def execute_sql_file(sql_file: Path) -> None:
    if not sql_file.exists():
        raise FileNotFoundError(f"Arquivo SQL não encontrado: {sql_file}")

    sql_content = sql_file.read_text(encoding="utf-8").strip()

    if not sql_content:
        print(f"Pulando SQL vazio: {sql_file.relative_to(PROJECT_ROOT)}")
        return

    print(f"Executando: {sql_file.relative_to(PROJECT_ROOT)}")

    if shutil.which("duckdb") is not None:
        subprocess.run(
            ["duckdb", str(DB_PATH), "-c", sql_content],
            text=True,
            cwd=PROJECT_ROOT,
            check=True,
        )
        return

    try:
        import duckdb as duckdb_module
    except ImportError as exc:
        raise RuntimeError(
            "DuckDB CLI não encontrado e o pacote Python 'duckdb' também não está disponível."
        ) from exc

    connection = duckdb_module.connect(str(DB_PATH))
    try:
        for statement in split_sql_statements(sql_content):
            if statement.strip():
                connection.execute(statement)
    finally:
        connection.close()


def recreate_database() -> None:
    ensure_duckdb_available()

    if DB_PATH.exists():
        print(f"Removendo banco anterior: {DB_PATH}")
        DB_PATH.unlink()

    print(f"Criando novo banco: {DB_PATH}")
    print()

    for sql_file in SQL_PHASES:
        execute_sql_file(sql_file)

    try:
        import duckdb as duckdb_module
    except ImportError as exc:
        raise RuntimeError("Não foi possível importar duckdb para gerar o relatório de qualidade.") from exc

    connection = duckdb_module.connect(str(DB_PATH))
    try:
        quality_report = connection.execute(
            """
            SELECT * FROM (
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
            ORDER BY tabela
            """
        ).fetchall()

        output_path = OUTPUTS_DIR / "checks" / "qualidade_dados.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as file_handle:
            file_handle.write("tabela,coluna,total_registros,valores_nulos,valores_duplicados\n")
            for row in quality_report:
                file_handle.write(
                    ",".join(str(value) for value in row) + "\n"
                )
    finally:
        connection.close()

    print()
    print("Banco recriado com sucesso.")
    print(f"Arquivo gerado: {DB_PATH}")


def main() -> None:
    os.chdir(PROJECT_ROOT)

    print("Projeto Censo 2022 - Belo Horizonte")
    print("Execução reproduzível com DuckDB")
    print()

    ensure_directories()
    ensure_required_csvs()
    recreate_database()

    print()
    print("Processo finalizado.")


if __name__ == "__main__":
    main()
