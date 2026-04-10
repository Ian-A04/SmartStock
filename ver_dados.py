from database import obter_conexao

conn, cursor = obter_conexao()

cursor.execute("SELECT * FROM produtos")

dados = cursor.fetchall()

print(dados)

conn.close()
