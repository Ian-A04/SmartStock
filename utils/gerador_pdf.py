from fpdf import FPDF
from database import obter_conexao

class NotaFiscalPDF(FPDF):
    def header(self):
        # Este método reconstrói o topo idêntico ao modelo comercial
        pass

def gerar_danfe(nota_id):
    with obter_conexao() as (conn, cursor):
        # 1. Busca dados agregados da nota e cliente
        cursor.execute("""
            SELECT n.data, c.nome, c.contato 
            FROM notas n
            LEFT JOIN clientes c ON n.cliente_id = c.id
            WHERE n.id = ?
        """, (nota_id,))
        dados_nota = cursor.fetchone()

        if not dados_nota:
            print("❌ Nota não encontrada!")
            return 
        
        data_nota, nome_cliente, contato_cliente = dados_nota
        nome_cliente = nome_cliente if nome_cliente else "Consumidor Final"
        contato_cliente = contato_cliente if contato_cliente else "Não Informado"

        # 2. Busca itens associados à nota
        cursor.execute("""
            SELECT p.id, p.nome, i.quantidade, i.preco
            FROM itens_nota i
            JOIN produtos p ON i.produto_id = p.id
            WHERE i.nota_id = ?
        """, (nota_id,))
        itens = cursor.fetchall()

        # 3. Inicialização e Configuração do Layout do PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_margins(10, 10, 10)
        
        # --- BLOCO 1: EMISSOR VS DADOS DA VENDA ---
        pdf.set_font("Arial", "B", 11)
        # Coluna da Esquerda (Emissor)
        pdf.cell(110, 5, "SMARTSTOQUE SISTEMAS LTDA", ln=0)
        # Coluna da Direita (Dados da Venda)
        pdf.cell(80, 5, f"Venda: {nota_id}", ln=1, align="R")
        
        pdf.set_font("Arial", "", 9)
        pdf.cell(110, 5, "Contato: (61) 99521-8360", ln=0)
        pdf.cell(80, 5, f"Data emissao: {data_nota}", ln=1, align="R")
        
        pdf.cell(110, 5, "Forma pagamento: a Vista", ln=0)
        pdf.cell(80, 5, f"Entrega: pronta entrega ({data_nota})", ln=1, align="R")
        
        pdf.ln(4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Linha divisória
        pdf.ln(4)

        # --- BLOCO 2: DADOS DO CLIENTE ---
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 5, "DADOS DO CLIENTE", ln=1)
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 5, f"Cliente: {nome_cliente}", ln=1)
        pdf.cell(190, 5, f"Fone/Contato: {contato_cliente}", ln=1)
        pdf.cell(190, 5, "Endereco: Nao Informado", ln=1)
        
        pdf.ln(4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Linha divisória
        pdf.ln(4)

        # --- BLOCO 3: TABELA DE ITENS (CABEÇALHO) ---
        pdf.set_font("Arial", "B", 9)
        # Altura padrão das células da tabela = 6
        pdf.cell(15, 6, "Codigo", border=1, align="C")
        pdf.cell(85, 6, "Descricao", border=1)
        pdf.cell(15, 6, "Qtde", border=1, align="C")
        pdf.cell(25, 6, "Preco Brut.", border=1, align="C")
        pdf.cell(20, 6, "Descto", border=1, align="C")
        pdf.cell(30, 6, "Total", border=1, ln=True, align="C")
        
        # --- BLOCO 4: PREENCHIMENTO DOS ITENS ---
        pdf.set_font("Arial", "", 9)
        total_bruto = 0
        total_itens_qtd = 0
        
        for item in itens:
            prod_id, nome_prod, qtd, preco_unit = item
            subtotal_item = qtd * preco_unit
            
            total_bruto += subtotal_item
            total_itens_qtd += qtd
            
            pdf.cell(15, 6, str(prod_id), border=1, align="C")
            pdf.cell(85, 6, f" {nome_prod}", border=1)
            pdf.cell(15, 6, str(qtd), border=1, align="C")
            pdf.cell(25, 6, f"R$ {preco_unit:.2f}", border=1, align="R")
            pdf.cell(20, 6, "0,00%", border=1, align="C") # Padrão sem desconto individual
            pdf.cell(30, 6, f"R$ {subtotal_item:.2f}", border=1, ln=True, align="R")

        # --- BLOCO 5: TOTAIS E FECHAMENTO ---
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        
        # Alinhando os totais de forma resumida na parte inferior
        pdf.cell(100, 6, f"Quantidade Total de Itens: {total_itens_qtd}", ln=0)
        pdf.cell(90, 6, f"Valor Total: R$ {total_bruto:.2f}", ln=1, align="R")
        
        # Rodapé de Emissão
        pdf.ln(10)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(190, 5, f"Gerado automaticamente em {data_nota} | SmartStoque", align="C")

        # 4. Salvando o arquivo
        nome_arquivo = f"nota_fiscal_{nota_id}.pdf"
        pdf.output(nome_arquivo)
        print(f"✅ {nome_arquivo} gerado com sucesso no novo formato!")