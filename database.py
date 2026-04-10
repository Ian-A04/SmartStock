import sqlite3
from contextlib import contextmanager

@contextmanager
def obter_conexao():
    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        conn.close()