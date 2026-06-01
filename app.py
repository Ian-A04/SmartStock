import os
import sqlite3
from flask import Flask, render_template, request, jsonify

# --- SUAS IMPORTAÇÕES ORIGINAIS ---
# Certifique-se de que a pasta 'utils' com o 'gerador_pdf.py' está na mesma pasta deste arquivo
from utils.gerador_pdf import gerar_danfe 

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simulando o ID do usuário que estava logado no seu app antigo
usuario_logado_id = 1 


# --- SEUS MÉTODOS ORIGINAIS DO BANCO DE DADOS (MANTIDOS) ---
def obter_conexao():
    # Ajuste o nome para o caminho do seu arquivo .db atual se necessário
    conn = sqlite3.connect("estoque.db")
    return conn

def buscar_clientes_do_banco():
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM clientes") # Substitua pela sua query real se for diferente
        return cursor.fetchall()

def buscar_produtos_do_banco():
    with obter_conexao() as conn:
        cursor = conn.cursor()
        # Buscando id, nome, quantidade e preço (conforme a estrutura que você usava)
        cursor.execute("SELECT id, nome, quantidade, preco, imagem FROM produtos") 
        return cursor.fetchall()


# ================= SERVINDO AS PÁGINAS HTML =================
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/vendas')
def vendas():
    return render_template('vendas.html')

@app.route('/produtos')
def produtos():
    return render_template('produtos.html')

@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')


# ================= PONTES (API) PARA O JAVASCRIPT =================

# 1. Rota que alimenta o Dropdown de Clientes da tela de vendas
@app.route('/api/clientes', methods=['GET'])
def api_listar_clientes():
    dados_bd = buscar_clientes_do_banco()
    # Transforma a tupla do banco em um JSON amigável para o JavaScript
    clientes = [{"id": c[0], "nome": c[1]} for c in dados_bd]
    return jsonify(clientes)

# 2. Rota que alimenta o Dropdown de Produtos da tela de vendas
@app.route('/api/produtos', methods=['GET'])
def api_listar_produtos():
    dados_bd = buscar_produtos_do_banco()
    # Transforma a tupla do banco [id, nome, qtd, preco, imagem] em JSON
    produtos = [{"id": p[0], "nome": p[1], "quantidade": p[2], "preco": p[3], "imagem": p[4]} for p in dados_bd]
    return jsonify(produtos)

# 3. Rota de Finalizar Venda (Sua lógica original convertida para Web)
@app.route('/api/vendas/confirmar', methods=['POST'])
def api_confirmar_venda():
    dados = request.json
    cliente_id = dados.get('cliente_id') # Pode vir nulo (Consumidor Final)
    carrinho = dados.get('carrinho', [])

    if not carrinho:
        return jsonify({"sucesso": False, "mensagem": "O carrinho está vazio!"}), 400

    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            
            # 1. Cria a nota fiscal no banco
            cursor.execute(
                "INSERT INTO notas (data, cliente_id, usuario_id) VALUES (date('now'), ?, ?)",
                (cliente_id if cliente_id else None, usuario_logado_id)
            )
            nota_id = cursor.lastrowid
            
            # 2. Insere os itens e abate do estoque (Sua lógica idêntica)
            for item in carrinho:
                cursor.execute(
                    "INSERT INTO itens_nota (nota_id, produto_id, quantity, preco) VALUES (?, ?, ?, ?)",
                    (nota_id, item['id'], item['quantidade'], item['preco'])
                )
                cursor.execute(
                    "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?",
                    (item['quantidade'], item['id'])
                )
            conn.commit()
        
        # 3. Chame a sua função original de gerar o PDF da DANFE!
        gerar_danfe(nota_id)

        return jsonify({"sucesso": True, "mensagem": f"Venda {nota_id} realizada e PDF gerado com sucesso!"})

    except Exception as ex:
        return jsonify({"sucesso": False, "mensagem": f"Erro no banco de dados: {str(ex)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)