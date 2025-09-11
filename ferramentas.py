import os

# Este é o nosso primeiro módulo de ferramentas.
# Cada função aqui é uma "habilidade" do Nexo.

def criar_arquivo_texto(nome_arquivo, conteudo=""):
    """
    Cria um arquivo de texto e, opcionalmente, escreve um conteúdo nele.

    Args:
        nome_arquivo (str): O nome do arquivo a ser criado.
        conteudo (str): O texto a ser escrito no arquivo (opcional).
    """
    try:
        with open(nome_arquivo, 'w') as arquivo:
            arquivo.write(conteudo)
        print(f"Nexo: Criei o arquivo '{nome_arquivo}'.")
    except Exception as e:
        print(f"Nexo: Erro ao criar o arquivo: {e}")

# Adicione outras ferramentas aqui no futuro, como:
# def pesquisar_no_google(query):
#    ...
# def gerar_imagem_com_ia(prompt):
#    ...
