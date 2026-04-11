from fpdf import FPDF
from database import obter_conexao

def gerar_danfe(nota_id):
    with obter_conexao() as (conn, cursor):
        #busca dados da nota
        cursor.execute("SELECT data FROM notas WHERE id = ?", (nota_id,))
        nota = cursor.fetchone()

    if not nota:
        print("Nota não encontrada!")
        conn.close()

        return
    
    data_nota = nota[0]

    #busca itens da nota
    cursor.execute("""
    SELECT produtos.nome, itens_nota.quantidade, itens_nota.preco
    FROM itens_nota.nota_id = ?
    """, (nota_id,))
    itens = cursor.fetchall()

    #config do pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    #cabeçalho
    pdf.cell(190, 10, "DANFE - RECIBO DE VENDA", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 10, f"NOTA ID: {nota_id}")
    pdf.cell(95, 10, f"DATA: {data_nota}", ln=True, align="R")
    pdf.line(10, 35, 200, 35)
    pdf.ln(10)

    #tabela itens
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 10, "Produto", border=1)
    pdf.cell(30, 10, "Qtd", border=1, align="C")
    pdf.cell(30, 10, "V. Unit", border=1, align="C")
    pdf.cell(30, 10, "Total", border=1, ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    total_geral = 0

    for item in itens:
        nome, qtd, preco = item
        total_item = qtd * preco
        total_geral += total_item

        pdf.cell(100, 10, str(nome), border=1)
        pdf.cell(30, 10, str(qtd), border=1, align="C")
        pdf.cell(30, 10, f"R$ {preco:.2f}", border=1, align="C")
        pdf.cell(30, 10, f"R$ {total_item:.2f}", border=1, ln=True, align="C")
    
    #totalizador
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"TOTAL DA NOTA: R$ {total_geral:.2f}", ln=True, align="R")

    #salva o arquivo
    nome_arquivo = f"nota_venda_{nota_id}.pdf"
    pdf.output(nome_arquivo)

    conn.close()
    print(f"\n PDF '{nome_arquivo}' gerado com sucesso!")
    