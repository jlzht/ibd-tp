import duckdb
con = duckdb.connect('database.duckdb')
print(con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main' ORDER BY table_name").fetchall())
