from database import obter_conexao
from datetime import datetime

def adicionar_produto(nome, codigo, preco, quantidade):

    conn, cursor = obter_conexao()

    cursor.execute("""
    INSERT INTO produtos (nome, codigo, preco, quantidade)
    VALUES (?, ?, ?, ?)
    """, (nome, codigo, preco, quantidade))

    conn.commit()
    conn.close()

    print("Produto cadastrado!")


def remover_produto(id_produto):

    conn, cursor = obter_conexao()

    cursor.execute("""
    DELETE FROM produtos
    WHERE id = ?
    """, (id_produto,))

    conn.commit()
    conn.close()

    print("Produto removido com sucesso!")
    
def listar_produtos():
    conn, cursor = obter_conexao()

    cursor.execute("SELECT * FROM produtos")

    produtos = cursor.fetchall()

    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")

    else:
        print("\n===== PRODUTOS =====")

        for produto in produtos:
            print("ID:", produto[0])
            print("Nome:", produto[1])
            print("Código:", produto[2])
            print("Preço:", produto[3])
            print("Quantidade:", produto[4])
            print("--------------------")

    conn.close()

def atualizar_produto(id_produto, nome, codigo, preco, quantidade):

    conn, cursor = obter_conexao()

    cursor.execute("""
    UPDATE produtos
    SET nome=?, codigo=?, preco=?, quantidade=?
    WHERE id=?
    """, (nome, codigo, preco, quantidade, id_produto))

    conn.commit()
    conn.close()

    print("Produto atualizado!")

def adicionar_estoque(id_produto, quantidade):

    conn, cursor = obter_conexao()

    cursor.execute("""
    UPDATE produtos
    SET quantidade = quantidade + ?
    WHERE id = ?
    """, (quantidade, id_produto))

    conn.commit()
    conn.close()

    print("Estoque atualizado!")


def criar_nota():

    conn, cursor = obter_conexao()

    data = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("INSERT INTO notas (data) VALUES (?)", (data,))

    nota_id = cursor.lastrowid

    conn.commit()
    conn.close()

    print("Nota criada:", nota_id)

    return nota_id

def adicionar_item_nota(nota_id, produto_id, quantidade):

    conn, cursor = obter_conexao()

    cursor.execute("SELECT preco FROM produtos WHERE id=?", (produto_id,))
    preco = cursor.fetchone()[0]

    cursor.execute("""
    INSERT INTO itens_nota (nota_id, produto_id, quantidade, preco)
    VALUES (?, ?, ?, ?)
    """, (nota_id, produto_id, quantidade, preco))

    conn.commit()
    conn.close()

    print("Item adicionado à nota!")

def verificar_estoque_baixo(limite=10):
    """Retorna lista de produtos que estão com estoque baixo."""
    conn, cursor = obter_conexao()

    cursor.execute("""
    SELECT id, nome, quantidade
    FROM produtos
    WHERE quantidade <= ?
    """, (limite,))

    alertas = cursor.fetchall()
    conn.close

    return alertas