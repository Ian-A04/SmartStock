from database import obter_conexao
import xml.etree.ElementTree as ET

def importar_nota_xml(arquivo):

    # conecta ao banco
    conn, cursor = obter_conexao()


    # abre o XML
    tree = ET.parse(arquivo)
    root = tree.getroot()

    for produto in root.iter("prod"):

        nome = produto.find("xProd").text
        quantidade = float(produto.find("qCom").text)
        preco = float(produto.find("vUnCom").text)

        # verifica se o produto já existe
        cursor.execute(
            "SELECT id, quantidade FROM produtos WHERE nome=?",
            (nome,)
        )

        resultado = cursor.fetchone()

        if resultado:

            id_produto = resultado[0]
            estoque_atual = resultado[1]

            novo_estoque = estoque_atual + quantidade

            cursor.execute(
                "UPDATE produtos SET quantidade=? WHERE id=?",
                (novo_estoque, id_produto)
            )

            print(f"Estoque atualizado: {nome}")

        else:

            cursor.execute("""
            INSERT INTO produtos (nome, codigo, preco, quantidade)
            VALUES (?, ?, ?, ?)
            """, (nome, "", preco, quantidade))

            print(f"Produto cadastrado: {nome}")

    conn.commit()
    conn.close()

    print("Importação finalizada!")
