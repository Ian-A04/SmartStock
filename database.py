import sqlite3

def conectar():
    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    return conn, cursor