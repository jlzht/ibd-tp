import os
import duckdb

def inicializar_banco():
    caminho_banco = 'bh_censo.duckdb'
    caminho_schema = 'schema.sql'
    
    if not os.path.exists(caminho_schema):
        return

    con = duckdb.connect(caminho_banco)
    
    try:
        with open(caminho_schema, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        con.execute(sql_script)
        
    except Exception as e:
        print(f"ERRO")
        
    finally:
        con.close()

if __name__ == "__main__":
    inicializar_banco()