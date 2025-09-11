# Importa o módulo 'os' para interagir com o sistema operacional.
# O 'os' permite que o nosso código execute comandos, como criar arquivos ou diretórios.
import os

def executar_comando(comando):
    """
    Executa um comando de sistema.

    Args:
        comando (str): O comando a ser executado.
    """
    try:
        # A função os.system() executa o comando no terminal.
        os.system(comando)
        print(f"Comando executado: '{comando}'")
    except Exception as e:
        print(f"Erro ao executar o comando: {e}")

def nexo():
    """
    O cérebro do Nexo.
    Permite que o usuário insira comandos para o agente executar.
    """
    print("Olá, eu sou Nexo. O que você gostaria de fazer?")
    print("Para sair, digite 'sair'.")

    while True:
        # Solicita um comando do usuário.
        comando = input("Nexo > ")

        # Condição de saída.
        if comando.lower() == 'sair':
            print("Desligando Nexo. Até mais!")
            break

        # Verifica se o comando não está vazio.
        if comando:
            # Chama a função para executar o comando.
            executar_comando(comando)
        else:
            print("Por favor, digite um comando válido.")

# A linha abaixo garante que a função nexo() seja chamada quando o script é executado.
if __name__ == "__main__":
    nexo()

