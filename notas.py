from database import obter_conexao

def listar_notas():
    with obter_conexao() as (conn, cursor):
        cursor.execute("SELECT * FROM notas")
        notas = cursor.fetchall()

        if not notas:
            print("Nenhuma nota encontrada")
        else:
            for nota in notas:
                print(f"Nota ID: {nota[0]} | Data: {nota[1]}") 
        conn.commit()                        

def ver_itens_nota(nota_id):
    with obter_conexao() as (conn, cursor):
        cursor.execute("""
        SELECT produtos.nome, itens_nota.quantidade, itens_nota.preco FROM itens_nota
        JOIN produtos ON itens_nota.produto_id = produtos.id WHERE itens_nota.nota_id = ?
        """, (nota_id,))
        itens = cursor.fetchall()

        if not itens:
            print("Nenhum itens encontrado nessa nota.")
        else:
            print(f"\nItens DA NOTA {nota_id}")
            total_nota = 0

            for item in itens:
                nome = item[0]
                quantidade = item[1]
                preco = item[2]

                total = quantidade * preco 
                total_nota += total

                print(f"{nome} | Qtd: {quantidade} | Preço: {preco} | Total: {total}")
        
        print(f"\nTOTAL DA NOTA: {total_nota}")
        conn.commit()

def cancelar_nota(nota_id):
    with obter_conexao() as (conn, cursor):
        #pega itens da nota
        cursor.execute("""
        SELECT produto_id, quantidade
        FROM itens_nota
        WHERE nota_id = ?
        """, (nota_id,))
        itens = cursor.fetchall()

        if not itens:
            print("Nota não encontrada ou não possui itens")
            return
    
        #devolve itens ao estoque
        for item in itens:
            produto_id = item[0]
            quantidade = item[1]

            cursor.execute("""
            UPDATE produtos
            SET quantidade = quantidade + ?
            WHERE id = ?
            """, (quantidade, produto_id))

            #remove itens da nota
            cursor.execute("""
            DELETE FROM itens_nota
            WHERE nota_id = ?
            """, (nota_id,))

            #remove a nota
            cursor.execute("""
            DELETE FROM notas
            WHERE id = ?
            """, (nota_id,))

            print(f"Nota {nota_id} cancelada com sucesso")
        conn.commit()