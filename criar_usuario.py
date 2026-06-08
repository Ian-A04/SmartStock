# Importa a função oficial do seu módulo de autenticação
from auth.auth import cadastrar_usuario

if __name__ == "__main__":
    print("=== GERADOR DE USUÁRIO DO SISTEMA ===")
    
    # Pode alterar as credenciais aqui se desejar
    novo_usuario = "ian"
    nova_senha = "123"
    
    print(f"Tentando criar o usuário '{novo_usuario}'...")
    
    # Executa a função que aplica o hash SHA-256 automaticamente antes de salvar
    cadastrar_usuario(novo_usuario, nova_senha)
    
    print("🔥 Processo finalizado. Verifique os logs acima para confirmar o sucesso.")