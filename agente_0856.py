import requests
import google.generativeai as genai
import os

# Configurações vindas do seu arquivo de chaves
GEMINI_KEY = "AIzaSyB7uJGYZlanQ-39ZhYS6ndk69HZik8lO98"
SUPABASE_URL = "https://jyfurrvkqrdkwtvtfzbw.supabase.co/rest/v1/nexo_memoria"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5ZnVycnZrcXJka3d0dnRmemJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5MTYzMjAsImV4cCI6MjA3MzQ5MjMyMH0.zuTYPgiy4PbsGdkG_rDX-YREhWcy225U2732Lq__Pno"

def agente_analista():
    print("🧠 AGENTE 0856: Iniciando Análise de Dados...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # 1. Busca os últimos dados coletados pelo Agente 0855
        response = requests.get(f"{SUPABASE_URL}?select=*&order=id.desc&limit=1", headers=headers)
        dados = response.json()

        if dados:
            contexto_bruto = dados[0].get('contexto', 'Sem dados')
            print(f"📊 Dados encontrados: {contexto_bruto}")

            # 2. Usa o Gemini para analisar o que foi coletado
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Como analista do projeto NexoGenesis, resuma este evento e sugira a próxima ação: {contexto_bruto}"
            analise = model.generate_content(prompt)

            print(f"💡 INSIGHT DA IA: {analise.text}")
            
            # 3. Salva a análise de volta no Supabase (Persistência de Inteligência)
            log_analise = {
                "contexto": "Relatório de Inteligência 0856",
                "codigo_gerado": f"ANÁLISE: {analise.text[:200]}..."
            }
            requests.post(SUPABASE_URL, headers=headers, json=log_analise)
            print("✅ Análise persistida com sucesso!")
        else:
            print("💤 Nenhum dado novo para analisar.")

    except Exception as e:
        print(f"❌ Erro na análise: {e}")

if __name__ == "__main__":
    agente_analista()
