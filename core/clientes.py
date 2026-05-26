from database import obter_conexao

def adicionar_cliente(nome, contato):
    """Cadastra um novo cliente no banco. O nome é obrigatório, o contato é opcional."""
    nome_limpo = nome.strip()
    # Se o contato for vazio ou cheio de espaços, define como 'Não Informado'
    contato_limpo = contato.strip() if contato else ""
    if not contato_limpo:
        contato_limpo = "Não Informado"
    
    # Validação rigorosa apenas para o nome
    if not nome_limpo:
        print("\n❌ Erro: O nome do cliente é obrigatório e não pode ser vazio!")
        return False

    with obter_conexao() as (conn, cursor):
        cursor.execute("""
            INSERT INTO clientes (nome, contato)
            VALUES (?, ?)
        """, (nome_limpo, contato_limpo))
        conn.commit()
    print(f"\n✅ Cliente '{nome_limpo}' cadastrado com sucesso!")
    return True

def listar_clientes():
    """Exibe todos os clientes cadastrados de forma organizada."""
    with obter_conexao() as (conn, cursor):
        cursor.execute("SELECT id, nome, contato FROM clientes")
        clientes = cursor.fetchall()

        if not clientes:
            print("\n📭 Nenhum cliente cadastrado.")
        else:
            print("\n" + "="*50)
            print(f"{'ID':<5} | {'NOME':<25} | {'CONTATO':<15}")
            print("="*50)
            for c in clientes:
                print(f"{c[0]:<5} | {c[1]:<25} | {c[2]:<15}")
            print("="*50)

def buscar_cliente_por_id(cliente_id):
    """Busca um cliente específico para validar antes de uma venda (Seguro contra None)."""
    with obter_conexao() as (conn, cursor):
        cursor.execute("SELECT nome FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()
        
        if cliente:
            return cliente[0]
        return None