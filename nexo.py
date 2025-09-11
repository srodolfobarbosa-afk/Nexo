import os
import sys
import json
import traceback
from ferramentas import (
    criar_arquivo_texto,
    pesquisar_na_internet,
    usar_gemini_para_tarefa,
    gerar_codigo_com_gemini,
    executar_codigo,
    ler_arquivo,
    resumir_arquivo,
    criar_pasta,
    analisar_erro_com_gemini
)

def nexo():
    print("Olá, eu sou Nexo. O que você gostaria de fazer?")
    print("Para sair, digite 'sair'.")
    print("Para analisar o último erro, digite 'analisar erro'.")
    
    ultimo_erro = None

    while True:
        try:
            comando = input("Nexo > ").lower().strip()
            
            if comando == "sair":
                print("Desligando Nexo. Até mais!")
                break
            
            if not comando:
                print("Por favor, digite um comando válido.")
                continue

            if "criar arquivo de texto" in comando:
                partes = comando.split(" ", 4)
                if len(partes) < 5:
                    print("Nexo: Por favor, especifique o nome do arquivo e o conteúdo. Ex: 'criar arquivo de texto meu_arquivo.txt Olá, mundo!'")
                else:
                    nome_arquivo = partes[3]
                    conteudo = partes[4]
                    criar_arquivo_texto(nome_arquivo, conteudo)

            elif "criar pasta" in comando:
                partes = comando.split(" ", 2)
                if len(partes) < 3:
                    print("Nexo: Por favor, especifique o nome da pasta. Ex: 'criar pasta minha_pasta'")
                else:
                    nome_pasta = partes[2]
                    criar_pasta(nome_pasta)
            
            # A função de salvar no supabase está comentada para evitar o erro.
            #elif "salvar no supabase" in comando:
            #    partes = comando.split(" ", 4)
            #    if len(partes) < 5:
            #        print("Nexo: Por favor, especifique a tabela e o JSON. Ex: 'salvar no supabase usuarios {\"nome\":\"João\"}'")
            #    else:
            #        tabela = partes[3]
            #        dados_json_str = partes[4]
            #        try:
            #            dados_json = json.loads(dados_json_str)
            #            salvar_no_supabase(tabela, dados_json)
            #        except json.JSONDecodeError:
            #            print("Nexo: Formato JSON inválido.")

            elif "pesquisar" in comando:
                termo_de_busca = comando.replace("pesquisar", "", 1).strip()
                if not termo_de_busca:
                    print("Nexo: Por favor, especifique o que você quer pesquisar.")
                else:
                    pesquisar_na_internet(termo_de_busca)

            elif "usar gemini para tarefa" in comando:
                prompt = comando.replace("usar gemini para tarefa", "", 1).strip()
                if not prompt:
                    print("Nexo: Por favor, especifique a tarefa.")
                else:
                    usar_gemini_para_tarefa(prompt)

            elif "gerar codigo" in comando:
                topico = comando.replace("gerar codigo", "", 1).strip()
                if not topico:
                    print("Nexo: Por favor, especifique o tópico para o código.")
                else:
                    gerar_codigo_com_gemini(topico)

            elif "executar" in comando:
                nome_arquivo = comando.replace("executar", "", 1).strip()
                if not nome_arquivo:
                    print("Nexo: Por favor, especifique o nome do arquivo a ser executado.")
                else:
                    executar_codigo(nome_arquivo)
            
            elif "ler arquivo" in comando:
                nome_arquivo = comando.replace("ler arquivo", "", 1).strip()
                if not nome_arquivo:
                    print("Nexo: Por favor, especifique o nome do arquivo a ser lido.")
                else:
                    conteudo = ler_arquivo(nome_arquivo)
                    if conteudo is not None:
                        print(conteudo)

            elif "resumir arquivo" in comando:
                nome_arquivo = comando.replace("resumir arquivo", "", 1).strip()
                if not nome_arquivo:
                    print("Nexo: Por favor, especifique o nome do arquivo para resumir.")
                else:
                    resumir_arquivo(nome_arquivo)

            elif "analisar erro" in comando:
                if ultimo_erro:
                    print(f"Nexo: Analisando o último erro... {ultimo_erro}")
                    analisar_erro_com_gemini(ultimo_erro, "Não há contexto de código disponível.")
                else:
                    print("Nexo: Nenhum erro foi capturado para análise.")
            
            else:
                print("Nexo: Desculpe, não entendi o comando. Tente novamente.")

        except Exception:
            ultimo_erro = traceback.format_exc()
            print(f"Nexo: Ocorreu um erro inesperado. Para analisar, digite 'analisar erro'.")
        
if __name__ == "__main__":
    nexo()