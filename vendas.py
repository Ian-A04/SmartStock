from database import obter_conexao
from datetime import datetime

def registrar_venda(produto_id, quantidade):

    with obter_conexao() as (conn, cursor):

        try:
            #busca o produto
            cursor.execute("""
            SELECT nome, preco, quantidade
            FROM produtos
            WHERE id = ?
            """, (produto_id,))
            produto = cursor.fetchone()

            if produto is None:
                print("Produto não encontrado.")
                return
        
            nome, preco, estoque = produto
            if estoque < quantidade:
                print("Estoque insuficiente.")
                return

            #criar nota
            data = datetime.now().strftime("%d/%m/%Y")
            cursor.execute("""
            INSERT INTO notas (data)
            VALUES (?)
            """, (data,))

            nota_id = cursor.lastrowid
            #inserir item da nota
            cursor.execute("""
            INSERT INTO itens_nota (nota_id, produto_id, quantidade, preco)
            VALUES (?, ?, ?, ?)
            """, (nota_id, produto_id, quantidade, preco))

            #att estoque
            cursor.execute("""
            UPDATE produtos 
            SET quantidade = quantidade - ?
            WHERE id = ?
            """, (quantidade, produto_id))
            conn.commit()

            print("Venda registrada com sucesso!")
            print(f"Nota Fiscal: {nota_id}")

        except Exception as erro:
            conn.rollback()
            print("Erro na venda:")
            print(erro)

