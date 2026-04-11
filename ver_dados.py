from database import obter_conexao

with obter_conexao() as (conn, cursor):
    cursor.execute("SELECT * FROM produtos")
    dados = cursor.fetchall()
    print(dados)
