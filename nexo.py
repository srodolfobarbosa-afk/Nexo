# Importa o módulo 'os' para interagir com o sistema operacional.
import os

# Define um dicionário para mapear intenções a comandos.
# Isso torna mais fácil adicionar novas habilidades no futuro.
# 'criar_arquivo' é a nossa intenção. A lista de palavras são os gatilhos.
INTENCOES = {
    'criar_arquivo': ['crie um arquivo', 'criar um arquivo', 'faça um arquivo', 'escreva um arquivo'],
    'escrever_no_arquivo': ['escreva no arquivo', 'adicione ao arquivo', 'coloque no arquivo']
}

def mapear_intencao(comando):
    """
    Tenta mapear a frase do usuário para uma intenção conhecida.

    Args:
        comando (str): A frase do usuário em linguagem natural.

    Returns:
        str: O nome da intenção (ex: 'criar_arquivo') ou None se não encontrar.
    """
    comando_lower = comando.lower()
    for intencao, palavras_chave in INTENCOES.items():
        for palavra in palavras_chave:
            if palavra in comando_lower:
                return intencao
    return None

def executar_comando_do_nexo(comando, intencao_detectada):
    """
    Executa a ação baseada na intenção detectada.
    Aqui é onde o Nexo realmente "faz" o que foi pedido.
    """
    if intencao_detectada == 'criar_arquivo':
        # Aqui, vamos extrair o nome do arquivo da frase.
        partes = comando.split()
        nome_arquivo = partes[-1]  # Pega a última palavra como o nome do arquivo
        os.system(f"touch {nome_arquivo}")  # 'touch' é um comando de terminal para criar um arquivo vazio
        print(f"Nexo: Criei o arquivo '{nome_arquivo}'.")

    # Podemos adicionar mais "elif" para novas intenções aqui no futuro.
    # Ex: elif intencao_detectada == 'pesquisar_google':
    
    else:
        print("Nexo: Desculpe, não entendi o que você quer fazer.")


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
            # Tenta encontrar a intenção do usuário.
            intencao = mapear_intencao(comando)
            
            if intencao:
                # Se a intenção for reconhecida, executa a ação.
                executar_comando_do_nexo(comando, intencao)
            else:
                # Se não, tenta o modo antigo (comando de terminal direto).
                try:
                    os.system(comando)
                    print(f"Comando executado: '{comando}'")
                except Exception as e:
                    print(f"Erro ao executar o comando: {e}")
        else:
            print("Por favor, digite um comando válido.")

if __name__ == "__main__":
    nexo()

