import sqlite3
import os
from contextlib import contextmanager

# Pega o caminho exato onde o database.py está rodando
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "estoque.db")

@contextmanager
def obter_conexao():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        conn.close()