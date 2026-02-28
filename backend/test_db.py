import psycopg2

try:
    conn = psycopg2.connect("postgresql://user:password@localhost:5433/cs360")
    print("Conexão bem sucedida!")
    conn.close()
except BaseException as e:
    print(e)
