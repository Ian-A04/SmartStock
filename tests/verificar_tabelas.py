from database import obter_conexao
import os

with obter_conexao() as (conn, cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()

    print("Tabelas no banco:")
    for t in tabelas:
        print(t[0])

    print(f"\nCaminho atual do projeto: {os.getcwdb()}")