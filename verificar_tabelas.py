from database import obter_conexao
import os

conn = obter_conexao()
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

tabelas = cursor.fetchall()

print("Tabelas no banco:")
for t in tabelas:
    print(t[0])

conn.close()

print(f"\nCaminho atual do projeto: {os.getcwdb()}")