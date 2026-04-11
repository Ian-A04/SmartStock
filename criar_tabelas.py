from database import obter_conexao

with obter_conexao () as (conn, cursor):
# tabela de produtos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR,
        codigo VARCHAR,
        preco REAL,
        quantidade INTEGER
    )
    """)

# tabela de notas fiscais
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT
    )
    """)

# tabela de itens da nota
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens_nota (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nota_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco REAL
    )
    """)
    conn.commit()
print("Tabelas criadas com sucesso!")
