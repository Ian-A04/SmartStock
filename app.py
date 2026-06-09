import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, url_for, send_file
from werkzeug.utils import secure_filename
from database import obter_conexao
import time
from utils.gerador_pdf import gerar_danfe

# --- IMPORTANTE: Se você ainda usar as funções de PDF, descomente a linha abaixo ---
# from utils.gerador_pdf import gerar_danfe 

app = Flask(__name__)

# --- CONFIGURAÇÃO PARA UPLOAD DE IMAGENS ---
# 1. Pega o caminho absoluto da pasta onde este app.py está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Junta o caminho absoluto com a pasta static/uploads
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Cria a pasta caso não exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= SERVINDO AS PÁGINAS HTML =================
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/caixa')
@app.route('/vendas')
def vendas():
    return render_template('vendas.html')

@app.route('/produtos')
def produtos():
    return render_template('produtos.html')

@app.route('/clientes')
def clientes():
    return render_template('cadastro_cliente.html')

@app.route('/logout')
def efetuar_logout():
    return jsonify({"sucesso": True, "mensagem": "Sessão encerrada com sucesso!"}), 200

# ================= ROTAS DE LOGIN =================
@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.json
    usuario = dados.get('usuario')
    senha = dados.get('senha')

    if not usuario or not senha:
        return jsonify({"sucesso": False, "mensagem": "Preencha todos os campos!"}), 400

    try:
        with obter_conexao() as (conn, cursor):
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
            resultado = cursor.fetchone()

            if resultado:
                return jsonify({
                    "sucesso": True,
                    "usuario_id": resultado[0],
                    "nome": usuario 
                })
            else:
                return jsonify({"sucesso": False, "mensagem": "Usuário ou senha incorretos!"}), 401
    except Exception as ex:
        return jsonify({"sucesso": False, "mensagem": f"Erro no banco de dados: {str(ex)}"}), 500

# ================= ROTAS DE PRODUTOS =================
@app.route('/api/produtos/cadastrar', methods=['POST'])
def cadastrar_produto():
    # Como agora enviamos arquivo (imagem), usamos request.form e request.files (FormData)
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    quantidade = request.form.get('quantidade')
    imagem_file = request.files.get('imagem') # Pega o arquivo da imagem

    if not nome or not preco or not quantidade:
        return jsonify({"sucesso": False, "mensagem": "Preencha nome, preço e quantidade!"}), 400

    caminho_imagem = None
    if imagem_file and imagem_file.filename != '':
        # Limpa o nome do arquivo para evitar bugs
        nome_seguro = secure_filename(imagem_file.filename)
        caminho_salvamento = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
        imagem_file.save(caminho_salvamento)
        # Salva o caminho que o HTML vai usar para exibir a imagem
        caminho_imagem = f"/{UPLOAD_FOLDER}/{nome_seguro}"
    else:
        # Se o usuário não enviou imagem, deixa nulo ou um caminho padrão
        caminho_imagem = None 

    try:
        with obter_conexao() as (conn, cursor):
            # 🔥 CORREÇÃO DA JOGADA: Geramos um código único baseado no tempo atual.
            # Exemplo de resultado: "WEB-1717594102"
            codigo_automatico = f"WEB-{int(time.time())}"

            # 🔥 QUERY ATUALIZADA: Inserimos a coluna 'codigo' e o valor correspondente
            cursor.execute(
                "INSERT INTO produtos (nome, codigo, preco, quantidade, imagem) VALUES (?, ?, ?, ?, ?)",
                (nome, codigo_automatico, float(preco), int(quantidade), caminho_imagem)
            )
            conn.commit()
            
        return jsonify({"sucesso": True, "mensagem": "Produto cadastrado com sucesso!"})
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": f"Erro ao cadastrar: {str(e)}"}), 500
    
@app.route('/api/atualizar_foto_produto/<int:id_produto>', methods=['POST'])
def atualizar_foto_produto(id_produto):
    try:
        # Verifica se o arquivo de imagem veio na requisição
        if 'imagem' not in request.files:
            return jsonify({"sucesso": False, "mensagem": "Nenhuma imagem selecionada."}), 400
            
        imagem = request.files['imagem']
        
        if imagem and imagem.filename != '':
            # Limpa o nome do arquivo e salva na pasta do servidor
            nome_arquivo = secure_filename(imagem.filename)
            caminho_salvar = os.path.join('/home/kuras/meushop/SmartStoque/static/img', nome_arquivo)
            imagem.save(caminho_salvar)
            
            # Atualiza apenas a coluna 'imagem' no banco de dados
            caminho_banco = f'/static/img/{nome_arquivo}'
            
            with obter_conexao() as (conn, cursor):
                cursor.execute("UPDATE produtos SET imagem = ? WHERE id = ?", (caminho_banco, id_produto))
                conn.commit()
                
            return jsonify({"sucesso": True, "mensagem": "Imagem atualizada!"})
            
        return jsonify({"sucesso": False, "mensagem": "Arquivo de imagem inválido."}), 400

    except Exception as ex:
        return jsonify({"sucesso": False, "mensagem": str(ex)}), 500
    
@app.route('/api/produtos', methods=['GET'])
def listar_produtos_api():
    try:
        with obter_conexao() as (conn, cursor):
            # Busca também a imagem
            cursor.execute("SELECT id, nome, preco, quantidade, imagem FROM produtos")
            produtos = [
                {
                    "id": p[0], 
                    "nome": p[1], 
                    "preco": float(p[2]), 
                    "quantidade": p[3],
                    "imagem": p[4] # Retorna a imagem
                } for p in cursor.fetchall()
            ]
        return jsonify(produtos)
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 500

@app.route('/api/produtos/editar/<int:id_produto>', methods=['POST'])
def editar_produto(id_produto):
    dados = request.json
    nome = dados.get('nome')
    preco = dados.get('preco')
    quantidade = dados.get('quantidade')

    if not nome or preco is None or quantidade is None:
        return jsonify({"sucesso": False, "mensagem": "Campos inválidos!"}), 400
    try:
        with obter_conexao() as (conn, cursor):
            cursor.execute("UPDATE produtos SET nome=?, preco=?, quantidade=? WHERE id=?", (nome, float(preco), int(quantidade), id_produto))
            conn.commit()
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado com sucesso!"})
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": f"Erro ao editar: {str(e)}"}), 500

# ================= ROTAS DE CLIENTES =================
@app.route('/api/clientes/cadastrar', methods=['POST'])
def cadastrar_cliente():
    dados = request.json
    nome = dados.get('nome')
    contato = dados.get('contato', 'Não Informado') 

    if not nome:
        return jsonify({"sucesso": False, "mensagem": "O nome do cliente é obrigatório!"}), 400
    try:
        with obter_conexao() as (conn, cursor):
            cursor.execute("INSERT INTO clientes (nome, contato) VALUES (?, ?)", (nome, contato))
            conn.commit()
        return jsonify({"sucesso": True, "mensagem": "Cliente cadastrado com sucesso!"})
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": f"Erro: {str(e)}"}), 500

@app.route('/api/clientes', methods=['GET'])
def api_listar_clientes():
    try:
        with obter_conexao() as (conn, cursor):
            cursor.execute("SELECT id, nome FROM clientes")
            clientes = [{"id": linha[0], "nome": linha[1]} for linha in cursor.fetchall()]
        return jsonify(clientes)
    except Exception as e:
        print(f"Erro ao buscar clientes: {e}")
        return jsonify([]), 500

# ================= ROTAS DE VENDAS =================
@app.route('/api/vendas/confirmar', methods=['POST'])
def confirmar_venda():
    dados = request.json
    cliente_id = dados.get('cliente_id') 
    usuario_id = dados.get('usuario_id') 
    carrinho = dados.get('carrinho', [])

    if not carrinho:
        return jsonify({"sucesso": False, "mensagem": "O carrinho está vazio!"}), 400

    try:
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        with obter_conexao() as (conn, cursor):
            # AGORA A TABELA NOTAS TEM O usuario_id, ENTÃO VAI FUNCIONAR!
            cursor.execute("""
                INSERT INTO notas (data, cliente_id, usuario_id) 
                VALUES (?, ?, ?)
            """, (data_atual, cliente_id, usuario_id))
            
            nota_id = cursor.lastrowid 

            for item in carrinho:
                cursor.execute("""
                    INSERT INTO itens_nota (nota_id, produto_id, quantidade, preco) 
                    VALUES (?, ?, ?, ?)
                """, (nota_id, item['id'], item['quantidade'], item['preco']))
                
                cursor.execute("""
                    UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?
                """, (item['quantidade'], item['id']))

            conn.commit()
            
        return jsonify({"sucesso": True, "venda_id": nota_id, "mensagem": "Venda finalizada com sucesso!"})
    
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": f"Erro interno: {str(e)}"}), 500

@app.route('/api/notas/download/<int:nota_id>', methods=['GET'])
def baixar_pdf(nota_id):
    try:
        # 1. Tenta gerar o PDF
        print(f"[*] Solicitado download da nota {nota_id}...")
        gerar_danfe(nota_id)
        
        # 2. Descobre o caminho EXATO da pasta principal do seu projeto
        diretorio_atual = os.path.dirname(os.path.abspath(__name__))
        nome_arquivo = f"nota_fiscal_{nota_id}.pdf"
        caminho_completo = os.path.join(diretorio_atual, nome_arquivo)
        
        print(f"[*] Procurando o arquivo em: {caminho_completo}")

        # 3. Verifica se o arquivo realmente existe lá
        if os.path.exists(caminho_completo):
            print("[*] Arquivo encontrado! Enviando para o navegador...")
            return send_file(caminho_completo, as_attachment=True, mimetype='application/pdf')
        else:
            print("[!] ERRO: O arquivo não está nessa pasta.")
            return jsonify({"sucesso": False, "mensagem": f"O arquivo PDF da nota {nota_id} não foi localizado no servidor."}), 404
            
    except Exception as e:
        print(f"[!] ERRO INTERNO AO GERAR PDF: {str(e)}")
        return jsonify({"sucesso": False, "mensagem": f"Erro interno ao gerar PDF: {str(e)}"}), 500
            
    except Exception as e:
        return f"Erro ao processar o PDF da DANFE: {str(e)}", 500
    
if __name__ == '__main__':
    app.run(debug=True)