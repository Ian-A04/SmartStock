from database import obter_conexao
from core.clientes import buscar_cliente_por_id
from utils.gerador_pdf import gerar_danfe

def finalizar_venda(usuario_id, carrinho):
    """
    Registra a venda no banco de dados associando o vendedor logado 
    e o cliente escolhido, dando baixa no estoque e gerando o PDF.
    """
    if not carrinho:
        print("\n⚠️ O carrinho está vazio. Não é possível finalizar a venda.")
        return

    print("\n--- FINALIZAÇÃO DA VENDA ---")
    id_cliente_input = input("Digite o ID do Cliente (ou aperte [ENTER] para Consumidor Final): ").strip()

    cliente_id = None
    nome_cliente = "Consumidor Final"

    # Se o vendedor digitou um ID, valida se ele existe no banco
    if id_cliente_input:
        try:
            id_convertido = int(id_cliente_input)
            nome_validado = buscar_cliente_por_id(id_convertido)
            if nome_validado:
                cliente_id = id_convertido
                nome_cliente = nome_validado
                print(f"🔹 Cliente identificado: {nome_cliente}")
            else:
                print("❌ ID de cliente não encontrado! A venda será registrada como Consumidor Final.")
        except ValueError:
            print("❌ ID inválido! A venda será registrada como Consumidor Final.")

    # Inicia a transação com o banco de dados
    with obter_conexao() as (conn, cursor):
        try:
            # 1. Cria o cabeçalho da nota com a data atual, ID do cliente e ID do vendedor
            cursor.execute("""
                INSERT INTO notas (data, cliente_id, usuario_id) 
                VALUES (date('now'), ?, ?)
            """, (cliente_id, usuario_id))
            
            nota_id = cursor.lastrowid

            # 2. Processa cada item do carrinho
            for item in carrinho:
                produto_id = item['id']
                quantidade_venda = item['quantidade']
                preco_unitario = item['preco']

                # Verifica se há estoque suficiente antes de abater
                cursor.execute("SELECT quantidade, nome FROM produtos WHERE id = ?", (produto_id,))
                prod_banco = cursor.fetchone()
                
                if not prod_banco or prod_banco[0] < quantidade_venda:
                    nome_prod = prod_banco[1] if prod_banco else "Produto Desconhecido"
                    print(f"❌ Falha: Estoque insuficiente para o produto '{nome_prod}'. Venda cancelada.")
                    conn.rollback() # Cancela tudo se faltar um produto
                    return

                # Insere o item na tabela de ligação itens_nota
                cursor.execute("""
                    INSERT INTO itens_nota (nota_id, produto_id, quantidade, preco)
                    VALUES (?, ?, ?, ?)
                """, (nota_id, produto_id, quantidade_venda, preco_unitario))

                # Atualiza o saldo do produto dando a baixa no estoque
                cursor.execute("""
                    UPDATE produtos 
                    SET quantidade = quantidade - ? 
                    WHERE id = ?
                """, (quantidade_venda, produto_id))

            # Se todos os itens foram processados com sucesso, grava permanentemente
            conn.commit()
            print(f"\n✅ Venda {nota_id} gravada com sucesso no banco de dados!")
            
            # 3. Dispara a geração automática da DANFE no novo formato comercial
            gerar_danfe(nota_id)

        except Exception as e:
            conn.rollback() # Segurança contra corrupção de dados
            print(f"❌ Erro crítico ao processar transação de venda: {e}")