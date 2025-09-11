import os
from ferramentas import criar_arquivo_texto # Importa a nossa nova habilidade

# Define um dicionário para mapear intenções a funções/habilidades.
INTENCOES = {
    'criar_arquivo': ['crie um arquivo', 'criar um arquivo', 'faça um arquivo', 'escreva um arquivo'],
}

def mapear_intencao(comando):
    """
    Tenta mapear a frase do usuário para uma intenção conhecida.
    """
    comando_lower = comando.lower()
    for intencao, palavras_chave in INTENCOES.items():
        for palavra in palavras_chave:
            if palavra in comando_lower:
                return intencao
    return None

def nexo():
    """
    O cérebro do Nexo, agora mais inteligente.
    """
    print("Olá, eu sou Nexo. O que você gostaria de fazer?")
    print("Para sair, digite 'sair'.")

    while True:
        comando = input("Nexo > ")

        if comando.lower() == 'sair':
            print("Desligando Nexo. Até mais!")
            break

        if comando:
            intencao = mapear_intencao(comando)
            
            if intencao == 'criar_arquivo':
                # Extrai o nome do arquivo da frase
                partes = comando.split()
                if len(partes) > 2: # Garante que haja pelo menos 3 palavras
                    nome_arquivo = partes[-1]
                    criar_arquivo_texto(nome_arquivo) # Chama a função do módulo ferramentas
                else:
                    print("Nexo: Por favor, especifique o nome do arquivo.")
            else:
                # Se não, tenta o modo antigo
                try:
                    os.system(comando)
                    print(f"Comando executado: '{comando}'")
                except Exception as e:
                    print(f"Erro ao executar o comando: {e}")
        else:
            print("Por favor, digite um comando válido.")

if __name__ == "__main__":
    nexo()

