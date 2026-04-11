from produtos import adicionar_produto, listar_produtos, adicionar_estoque, remover_produto, verificar_estoque_baixo
from vendas import registrar_venda
from notas import listar_notas, ver_itens_nota, cancelar_nota
from relatorios import relatorio_vendas
from gerador_pdf import gerar_danfe
#--------------------------------------------------------------------------------------------------------------------

def menu():

    while True:
        try:
            #BLOCO DE ALERTA 
            alertas = verificar_estoque_baixo(10) #10 = estoque crítico
            if alertas:
                print("\n⚠️ ATENÇÃO: PRODUTOS COM ESTOQUE BAICO!")
                for item in alertas:
                    print(f"  - {item[1]} (ID: {item[0]}) possui apenas {item[2]} unidades.")
                print("-" * 30)
        
        except:
            pass
#-----------------------------------------------------------------------------------------    
        
        #MENU CRUD
        print("\n==== SISTEMA DE ESTOQUE ====")
        print("1 - Cadastrar Produto")
        print("2 - Listar Produtos")
        print("3 - Adicionar Estoque")
        print("4 - Remover Produto")
        print("5 - Registrar Venda")
        print("6 - Ver Notas")
        print("7 - Ver Itens da Nota")
        print("8 - Cancelar Nota")
        print("9 - Relatório de Vendas")
        print("10 - Gerar PDF da nota da venda (DANFE)")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

#----------------------------------------------------------------------------------------
        try:

            if opcao == "1":
                nome = input("Nome do produto: ")
                codigo = input("Código do produto: ")
                preco = float(input("Preço: "))
                quantidade = int(input("Quantidade inicial: "))

                adicionar_produto(nome, codigo, preco, quantidade)

            elif opcao == "2":
                listar_produtos()

            elif opcao == "3":
                produto_id = int(input("ID do produto: "))
                quantidade = int(input("Quantidade a adicionar: "))

                adicionar_estoque(produto_id, quantidade)

            elif opcao == "4":
                produto_id = int(input("ID do produto para remover: "))
                confirmar = input("Tem certeza? (s/n): ")

                if confirmar.lower() == "s":
                    remover_produto(produto_id)
                elif confirmar.lower() == "n":
                    print("Operação cancelada.")
                else:
                    print("Opção inválida.")

            elif opcao == "5":
                produto_id = int(input("ID do produto: "))
                quantidade = int(input("Quantidade vendida: "))

                registrar_venda(produto_id, quantidade)

            elif opcao == "6":
                listar_notas()

            elif opcao == "7":
                nota_id = int(input("ID da nota: "))
                ver_itens_nota(nota_id)

            elif opcao == "8":
                nota_id = int(input("ID da nota para cancelar: "))
                confirmar = input("Tem certeza que deseja cancelar? (s/n): ")

                if confirmar.lower() == "s":
                    cancelar_nota(nota_id)
                elif confirmar.lower() == "n":
                    print("Operação cancelada.")
                else:
                    print("Opção inválida.")

            elif opcao == "9":
                relatorio_vendas()

            elif opcao == "10":
                id_nota = int(input("Digite o ID da nota: "))
                gerar_danfe(id_nota)

            elif opcao == "0":
                print("Saindo do sistema...")
                break

            else:
                print("Opção inválida!")

        except ValueError:
            print("Erro: digite apenas números onde for solicitado.")

        except Exception as erro:
            print("Erro inesperado:", erro)

menu()