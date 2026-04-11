import sqlite3

conn = sqlite3.connect("estoque.db")

print("Banco criado com sucesso!")

conn.close()
