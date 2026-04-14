from database import obter_conexao

def inicializar_banco():
    with obter_conexao() as (conn, cursor):
        # 1. Tabela de Produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                codigo TEXT UNIQUE NOT NULL,
                preco REAL NOT NULL,
                quantidade INTEGER NOT NULL
            )
        """)

        # 2. Tabela de Clientes (Nova!)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                contato TEXT NOT NULL
            )
        """)

        # 3. Tabela de Usuários (Login e Cadastro!)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        """)

        # 4. Tabela de Notas (Com vínculo ao Cliente)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                cliente_id INTEGER,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
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
                FOREIGN KEY (nota_id) REFERENCES notas (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
        """)

        # Tenta adicionar a coluna cliente_id caso a tabela notas já exista
        try:
            cursor.execute("ALTER TABLE notas ADD COLUMN cliente_id INTEGER REFERENCES clientes(id)")
        except:
            pass

        conn.commit()
    print("✅ Banco de Dados atualizado: Tabelas de Clientes e Usuários prontas!")

if __name__ == "__main__":
    inicializar_banco()