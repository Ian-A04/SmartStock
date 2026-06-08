from database import obter_conexao

def inicializar_banco():
    with obter_conexao() as (conn, cursor):
        # 1. Tabela de Produtos (Unificada: Código + Imagem)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                codigo TEXT UNIQUE NOT NULL,
                preco REAL NOT NULL,
                quantidade INTEGER NOT NULL,
                imagem TEXT
            )
        """)

        # 2. Tabela de Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                contato TEXT NOT NULL
            )
        """)

        # 3. Tabela de Usuários (Vendedores)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nome_completo TEXT NOT NULL DEFAULT 'Vendedor Padrão',
                telefone TEXT DEFAULT '(00) 00000-0000'
            )
        """)

        # 4. Tabela de Notas (Vendas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                cliente_id INTEGER,
                usuario_id INTEGER,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)

        # 5. Tabela de Itens da Nota
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_nota (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nota_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL,
                FOREIGN KEY (nota_id) REFERENCES notas(id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)

        # --- Camada de Compatibilidade / Migrações ---
        # Se você rodar esse script em um banco antigo, ele adiciona as colunas novas sem dar erro
        try:
            cursor.execute("ALTER TABLE produtos ADD COLUMN imagem TEXT")
        except:
            pass  # Se a coluna já existia, ignora o erro

        try:
            cursor.execute("ALTER TABLE notas ADD COLUMN cliente_id INTEGER REFERENCES clientes(id)")
        except:
            pass

        try:
            cursor.execute("ALTER TABLE notas ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)")
        except:
            pass

        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN nome_completo TEXT NOT NULL DEFAULT 'Vendedor Padrão'")
        except:
            pass

        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN telefone TEXT DEFAULT '(00) 00000-0000'")
        except:
            pass

        conn.commit()
    print("✅ Banco de Dados estruturado e atualizado com sucesso!")

if __name__ == "__main__":
    inicializar_banco()