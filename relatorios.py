from database import obter_conexao

def relatorio_vendas():

    conn, cursor = obter_conexao()

    cursor.execute("""
    SELECT produtos.nome,
        SUM(itens_nota.quantidade),
        SUM(itens_nota.quantidade * itens_nota.preco)
    FROM itens_nota JOIN produtos ON itens_nota.produto_id = produtos.id
    GROUP BY produtos.nome
    """)

    vendas = cursor.fetchall()

    if not vendas:
        print("Nenhuma venda registrada.")
    else:
        print("\nRELATÓRIO DE VENDAS\n")

        for venda in vendas:
                
            nome = venda[0]
            quantidade = venda[1]
            total = venda[2]

            print(f"Produto: {nome}")
            print(f"Quantidade Vendida: {quantidade}")
            print(f"Valor Total Vendido: {total:.2f}")
            print("-----------------------")

    conn.close()
