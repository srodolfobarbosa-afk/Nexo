import os
import subprocess
import google.generativeai as genai
from googleapiclient.discovery import build
from supabase import create_client, Client
from dotenv import load_dotenv

# Força a leitura do .env a partir do diretório do script, garantindo que ele sempre seja encontrado.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# ==================== Variáveis de Configuração ====================
API_KEY_GEMINI = os.getenv('GOOGLE_API_KEY')
API_KEY_GOOGLE_SEARCH = os.getenv('GOOGLE_SEARCH_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')


# Configurações de API e modelos
genai.configure(api_key=API_KEY_GEMINI)
model = genai.GenerativeModel('gemini-1.5-flash')

# ==================== Funções de Ferramentas ====================
def testar_conexao_supabase():
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Nexo: Chaves do Supabase não encontradas no arquivo .env.")
            return None
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Nexo: Conexão com o Supabase estabelecida com sucesso.")
        return supabase_client
    except Exception as e:
        print(f"Nexo: Erro ao conectar ao Supabase: {e}")
        return None

def salvar_no_supabase(tabela, dados):
    supabase_client = testar_conexao_supabase()
    if not supabase_client:
        print("Nexo: Não foi possível salvar dados. Conexão com Supabase falhou.")
        return None
    try:
        response = supabase_client.table(tabela).insert(dados).execute()
        print("Nexo: Dados salvos com sucesso no Supabase.")
        return response
    except Exception as e:
        print(f"Nexo: Erro ao salvar dados no Supabase: {e}")
        return None
        
def ler_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None

def criar_arquivo_texto(nome_arquivo, conteudo=''):
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"Nexo: Arquivo '{nome_arquivo}' criado com sucesso.")
    except Exception as e:
        print(f"Erro ao criar o arquivo: {e}")

def criar_pasta(nome_pasta):
    try:
        os.makedirs(nome_pasta, exist_ok=True)
        print(f"Nexo: Pasta '{nome_pasta}' criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar a pasta: {e}")

def pesquisar_na_internet(termo_de_busca):
    if not API_KEY_GOOGLE_SEARCH or not CSE_ID:
        print("Nexo: Chaves de API do Google Search não estão configuradas.")
        return "Nexo: Erro de configuração."
        
    try:
        service = build("customsearch", "v1", developerKey=API_KEY_GOOGLE_SEARCH)
        res = service.cse().list(
            q=termo_de_busca,
            cx=CSE_ID,
            num=5
        ).execute()

        resultados_formatados = ""
        for item in res.get('items', []):
            title = item.get('title')
            snippet = item.get('snippet')
            link = item.get('link')
            resultados_formatados += f"Título: {title}\nLink: {link}\nDescrição: {snippet}\n\n"
        print(resultados_formatados)
        return resultados_formatados
    except Exception as e:
        print(f"Nexo: Ocorreu um erro durante a pesquisa: {e}")
        return None

def usar_gemini_para_tarefa(prompt, contexto=""):
    if not API_KEY_GEMINI:
        print("Nexo: A chave de API do Gemini não está configurada.")
        return
    try:
        full_prompt = f"{prompt}\n\n{contexto}" if contexto else prompt
        response = model.generate_content(full_prompt)
        print(f"Nexo: {response.text}")
    except Exception as e:
        print(f"Nexo: Ocorreu um erro ao usar o Gemini: {e}")

def gerar_codigo_com_gemini(topico):
    if not API_KEY_GEMINI:
        print("Nexo: A chave de API do Gemini não está configurada.")
        return
    prompt_codigo = f"Gere um código em Python sobre '{topico}'. Inclua comentários e use boas práticas de programação. Não use nenhum texto de introdução ou conclusão. Apenas o código."
    try:
        response = model.generate_content(prompt_codigo)
        codigo_gerado = response.text
        nome_arquivo = f"{topico.replace(' ', '_')}.py"
        criar_arquivo_texto(nome_arquivo, codigo_gerado)
        print(f"Nexo: Código gerado e salvo em '{nome_arquivo}'.")
    except Exception as e:
        print(f"Nexo: Ocorreu um erro ao gerar o código: {e}")

def executar_codigo(nome_arquivo):
    if not nome_arquivo.endswith('.py'):
        nome_arquivo += '.py'
    if not os.path.exists(nome_arquivo):
        print(f"Nexo: O arquivo '{nome_arquivo}' não foi encontrado.")
        return
    try:
        print(f"Nexo: Executando '{nome_arquivo}'...")
        process = subprocess.run(['python', nome_arquivo], capture_output=True, text=True, check=True, encoding='utf-8')
        print("--- Saída do Programa ---")
        print(process.stdout)
        if process.stderr:
            print("--- Erros ---")
            print(process.stderr)
        print("-------------------------")
    except subprocess.CalledProcessError as e:
        print(f"Nexo: Erro ao executar o arquivo '{nome_arquivo}'.")
        print("--- Saída de Erro ---")
        print(e.stderr)
        print("---------------------")
    except Exception as e:
        print(f"Nexo: Ocorreu um erro inesperado: {e}")

def resumir_arquivo(nome_arquivo):
    conteudo_do_arquivo = ler_arquivo(nome_arquivo)
    if conteudo_do_arquivo:
        print("Nexo: Conteúdo lido com sucesso. Enviando para o Gemini para resumo...")
        usar_gemini_para_tarefa("Resuma o seguinte texto de forma concisa e clara:", conteudo_do_arquivo)
    else:
        print(f"Nexo: Não foi possível ler o arquivo '{nome_arquivo}'.")

def analisar_erro_com_gemini(mensagem_erro, codigo_contexto="Não há contexto de código disponível."):
    print("Nexo: Ocorreu um erro! Analisando o problema...")
    
    prompt_analise = f"""
    Análise do erro:
    O programa Python encontrou o seguinte erro:
    {mensagem_erro}

    O contexto do código onde o erro ocorreu é:
    {codigo_contexto}

    Com base nesta informação, identifique a causa do erro e forneça o trecho de código corrigido.
    Responda apenas com o código Python corrigido e uma breve explicação do que foi alterado.
    """
    
    if not API_KEY_GEMINI:
        print("Nexo: A chave de API do Gemini não está configurada.")
        return

    try:
        response = model.generate_content(prompt_analise)
        print("Nexo: Análise do Gemini:")
        print(response.text)
    except Exception as e:
        print(f"Nexo: Ocorreu um erro ao tentar analisar o problema: {e}")