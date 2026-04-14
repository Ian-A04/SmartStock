import hashlib
from database import obter_conexao

def gerar_hash(senha):
    # Transforma a senha em um código seguro
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar_usuario(usuario, senha):
    with obter_conexao() as (conn, cursor):
        try:
            senha_hash = gerar_hash(senha)
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha_hash))
            conn.commit()
            print(f"Usuário {usuario} cadastrado!")
        except:
            print("Erro: Este nome de usuário já existe.")

def fazer_login(usuario, senha):
    with obter_conexao() as (conn, cursor):
        senha_hash = gerar_hash(senha)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha_hash))
        return cursor.fetchone() is not None