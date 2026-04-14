from database import obter_conexao

def adicionar_cliente(nome, contato):
    """Cadastra um novo cliente no banco de dados."""
    with obter_conexao() as (conn, cursor):
        cursor.execute("""
            INSERT INTO clientes (nome, contato)
            VALUES (?, ?)
        """, (nome, contato))
        conn.commit()
    print(f"\n✅ Cliente '{nome}' cadastrado com sucesso!")

def listar_clientes():
    """Exibe todos os clientes cadastrados."""
    with obter_conexao() as (conn, cursor):
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()

        if not clientes:
            print("\n📭 Nenhum cliente cadastrado.")
        else:
            print("\n" + "="*30)
            print("       LISTA DE CLIENTES")
            print("="*30)
            for c in clientes:
                print(f"ID: {c[0]} | Nome: {c[1]} | Contato: {c[2]}")
            print("="*30)

def buscar_cliente_por_id(cliente_id):
    """Busca um cliente específico para validar antes de uma venda."""
    with obter_conexao() as (conn, cursor):
        cursor.execute("SELECT nome FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()
        return cliente[0] if cliente else None