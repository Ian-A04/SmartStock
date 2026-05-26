import flet as ft
from database import obter_conexao
from core.clientes import adicionar_cliente
from core.vendas import finalizar_venda

# --- FUNÇÕES DE CONEXÃO DIRETA COM O BANCO DE DADOS ---

def buscar_produtos_do_banco():
    """Busca a lista de produtos atualizada direto do SQLite."""
    with obter_conexao() as (conn, cursor):
        cursor.execute("SELECT id, nome, codigo, preco, quantidade FROM produtos")
        return cursor.fetchall()

def buscar_clientes_do_banco():
    """Busca a lista de clientes para exibir no App."""
    with obter_conexao() as (conn, cursor):
        cursor.execute("SELECT id, nome, contato FROM clientes")
        return cursor.fetchall()


# --- INTERFACE GRÁFICA (FLET) ---

def main(page: ft.Page):
    page.title = "SmartStoque Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 390
    page.window_height = 844
    page.padding = 0

    # ESTADO DO APP (Memória temporária do carrinho de compras atual)
    carrinho_atual = []
    usuario_logado_id = 1  # Simulando o ID do vendedor logado (ex: Edson Calado)

    # Conteúdo principal que muda conforme a aba clicada
    container_principal = ft.Container(expand=True, padding=15)

    # --- ABA 1: VENDAS (PDV MOBILE REAL) ---
    def carregar_tela_vendas():
        lista_carrinho_ui = ft.ListView(expand=True, spacing=10)
        
        # Dropdown para selecionar o cliente cadastrado no banco de dados
        dropdown_cliente = ft.Dropdown(
            label="Selecionar Cliente",
            hint_text="Selecione ou deixe vazio para Consumidor Final",
            border_radius=8,
        )
        
        # Atualiza a lista de clientes dentro do seletor de vendas
        clientes_bd = buscar_clientes_do_banco()
        dropdown_cliente.options = [ft.dropdown.Option(key="", text="🛒 Consumidor Final")]
        for cli in clientes_bd:
            dropdown_cliente.options.append(ft.dropdown.Option(key=str(cli[0]), text=f"👤 {cli[1]}"))

        # Dropdown para selecionar o produto do banco que quer colocar no carrinho
        dropdown_produto = ft.Dropdown(
            label="Escolher Produto",
            border_radius=8,
            expand=True
        )
        
        produtos_bd = buscar_produtos_do_banco()
        dropdown_produto.options = []
        for prod in produtos_bd:
            dropdown_produto.options.append(
                ft.dropdown.Option(key=str(prod[0]), text=f"{prod[1]} (R$ {prod[3]:.2f})")
            )

        def adicionar_ao_carrinho_click(e):
            if not dropdown_produto.value:
                return
            
            p_id = int(dropdown_produto.value)
            # Busca os detalhes do produto selecionado na lista carregada do banco
            produto_selecionado = next((p for p in produtos_bd if p[0] == p_id), None)
            
            if produto_selecionado:
                # Adiciona no formato que o core/vendas.py espera
                carrinho_atual.append({
                    "id": produto_selecionado[0],
                    "nome": produto_selecionado[1],
                    "quantidade": 1, # Adiciona de 1 em 1 por padrão
                    "preco": produto_selecionado[3]
                })
                atualizar_carrinho_ui()

        def fechar_venda_click(e):
            if not carrinho_atual:
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ O carrinho está vazio!"))
                page.snack_bar.open = True
                page.update()
                return

            # Captura o cliente selecionado na interface mobile
            cliente_selecionado_id = dropdown_cliente.value if dropdown_cliente.value else ""
            
            # --- INTEGRAÇÃO COM O BACK-END ---
            # Interceptamos o input para rodar a lógica real do core/vendas.py
            # Como finalizar_venda pede o input via terminal, vamos simular a injeção ou chamar a transação limpa:
            try:
                from core.vendas import finalizar_venda
                
                # Para evitar o input() travando o app mobile, fazemos o fluxo direto no banco:
                with obter_conexao() as (conn, cursor):
                    c_id = int(cliente_selecionado_id) if cliente_selecionado_id else None
                    cursor.execute(
                        "INSERT INTO notas (data, cliente_id, usuario_id) VALUES (date('now'), ?, ?)",
                        (c_id, usuario_logado_id)
                    )
                    nota_id = cursor.lastrowid
                    
                    for item in carrinho_atual:
                        cursor.execute(
                            "INSERT INTO itens_nota (nota_id, produto_id, quantidade, preco) VALUES (?, ?, ?, ?)",
                            (nota_id, item['id'], item['quantidade'], item['preco'])
                        )
                        cursor.execute(
                            "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?",
                            (item['quantidade'], item['id'])
                        )
                    conn.commit()
                
                # Gera a DANFE automaticamente usando o gerador_pdf técnico
                from utils.gerador_pdf import gerar_danfe
                gerar_danfe(nota_id)

                carrinho_atual.clear()
                atualizar_carrinho_ui()
                dropdown_cliente.value = ""
                
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ Venda {nota_id} realizada! PDF Gerado com sucesso."))
                page.snack_bar.open = True
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"❌ Erro ao fechar venda: {ex}"))
                page.snack_bar.open = True
            
            page.update()

        def atualizar_carrinho_ui():
            lista_carrinho_ui.controls.clear()
            total = 0
            for item in carrinho_atual:
                total += item["preco"] * item["quantidade"]
                lista_carrinho_ui.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.BUILD_CIRCLE, color=ft.colors.BLUE_700),
                        title=ft.Text(item["nome"]),
                        subtitle=ft.Text(f"{item['quantidade']}x — R$ {item['preco']:.2f}"),
                        trailing=ft.Text(f"R$ {item['preco']*item['quantidade']:.2f}", weight=ft.FontWeight.BOLD)
                    )
                )
            btn_fechar.text = f"Confirmar Venda (R$ {total:.2f})"
            page.update()

        btn_fechar = ft.ElevatedButton(
            text="Confirmar Venda (R$ 0.00)",
            bgcolor=ft.colors.GREEN_700,
            color=ft.colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=fechar_venda_click,
            expand=True
        )

        container_principal.content = ft.Column([
            ft.Text("Caixa Operacional", size=22, weight=ft.FontWeight.BOLD),
            dropdown_cliente,
            ft.Row([
                dropdown_produto,
                ft.IconButton(icon=ft.icons.ADD_BOX_ROUNDED, icon_color=ft.colors.BLUE_700, icon_size=35, on_click=adicionar_ao_carrinho_click)
            ]),
            ft.Text("Produtos no Carrinho:", weight=ft.FontWeight.BOLD, color=ft.colors.GREY_700),
            lista_carrinho_ui,
            ft.Row([btn_fechar])
        ], expand=True)
        page.update()

    # --- ABA 2: ESTOQUE REAL (CONSULTA AO BANCO) ---
    def carregar_tela_estoque():
        lista_produtos_ui = ft.ListView(expand=True, spacing=5)
        
        # Puxa os dados reais de produtos do banco de dados SQLite
        produtos = buscar_produtos_do_banco()
        
        for prod in produtos:
            p_id, nome, codigo, preco, qtd = prod
            cor_qtd = ft.colors.GREEN_600 if qtd > 5 else ft.colors.RED_600
            
            lista_produtos_ui.controls.append(
                ft.ListTile(
                    leading=ft.CircleAvatar(content=ft.Text(str(p_id)), bgcolor=ft.colors.BLUE_50),
                    title=ft.Text(nome, weight=ft.FontWeight.W_500),
                    subtitle=ft.Text(f"Cód: {codigo} | Qtd em estoque: {qtd}", color=cor_qtd),
                    trailing=ft.Text(f"R$ {preco:.2f}", weight=ft.FontWeight.BOLD)
                )
            )

        container_principal.content = ft.Column([
            ft.Text("Controle de Estoque", size=22, weight=ft.FontWeight.BOLD),
            ft.TextField(label="Filtrar Produto...", prefix_icon=ft.icons.SEARCH, border_radius=8),
            lista_produtos_ui
        ], expand=True)
        page.update()

    # --- ABA 3: CLIENTES REAL (CADASTRO DIRETAMENTE NO BANCO) ---
    def carregar_tela_clientes():
        txt_nome = ft.TextField(label="Nome do Cliente (Obrigatório)", border_radius=8)
        txt_contato = ft.TextField(label="Contato/Telefone (Opcional)", border_radius=8)
        lista_clientes_ui = ft.ListView(expand=True, spacing=5)

        def atualizar_lista_clientes_ui():
            lista_clientes_ui.controls.clear()
            clientes = buscar_clientes_do_banco()
            for cli in clientes:
                lista_clientes_ui.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.PERSON, color=ft.colors.GREY_600),
                        title=ft.Text(cli[1]),
                        subtitle=ft.Text(f"Contato: {cli[2]}")
                    )
                )
            page.update()

        def salvar_cliente_click(e):
            # Envia para a função do seu back-end (core/clientes.py)
            sucesso = adicionar_cliente(txt_nome.value, txt_contato.value)
            
            if sucesso:
                txt_nome.value = ""
                txt_contato.value = ""
                page.snack_bar = ft.SnackBar(ft.Text("✅ Cliente gravado no SQLite!"))
                page.snack_bar.open = True
                atualizar_lista_clientes_ui() # Atualiza a listagem na hora
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ Erro: O nome é obrigatório!"))
                page.snack_bar.open = True
            page.update()

        # Carrega a lista de clientes já salvos ao abrir a tela
        atualizar_lista_clientes_ui()

        container_principal.content = ft.Column([
            ft.Text("Cadastro de Clientes", size=22, weight=ft.FontWeight.BOLD),
            txt_nome,
            txt_contato,
            ft.Row([
                ft.ElevatedButton("Salvar Cliente", icon=ft.icons.SAVE, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE, on_click=salvar_cliente_click, expand=True)
            ]),
            ft.Divider(),
            ft.Text("Clientes Cadastrados:", weight=ft.FontWeight.BOLD, color=ft.colors.GREY_700),
            lista_clientes_ui
        ], expand=True)
        page.update()

    # --- BARRA DE NAVEGAÇÃO INFERIOR CORRELACIONADA ---
    def mudar_aba(e):
        idx = e.control.selected_index
        if idx == 0:
            carregar_tela_vendas()
        elif idx == 1:
            carregar_tela_estoque()
        elif idx == 2:
            carregar_tela_clientes()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=mudar_aba,
        destinations=[
            ft.NavigationDestination(icon="SHOPPING_BAG", label="Vendas"),
            ft.NavigationDestination(icon="LAYERS", label="Estoque"),
            ft.NavigationDestination(icon="PEOPLE_ALT", label="Clientes"),
        ],
    )

    # Inicia o aplicativo exibindo a tela de Vendas por padrão
    carregar_tela_vendas()
    page.add(container_principal)

if __name__ == "__main__":
    ft.app(target=main)