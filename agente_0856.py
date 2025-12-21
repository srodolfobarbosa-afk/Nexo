import requests
import google.generativeai as genai
import os

# USANDO A CHAVE QUE FUNCIONOU NO SCAN
GEMINI_KEY = "AIzaSyDrbRaS9jRRczo5gs6tMwfeR88LofOLHqE"
SUPABASE_URL = "https://jyfurrvkqrdkwtvtfzbw.supabase.co/rest/v1/nexo_memoria"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5ZnVycnZrcXJka3d0dnRmemJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5MTYzMjAsImV4cCI6MjA3MzQ5MjMyMH0.zuTYPgiy4PbsGdkG_rDX-YREhWcy225U2732Lq__Pno"

def agente_analista():
    print("🧠 AGENTE 0856: Iniciando Análise de Dados...")
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.get(f"{SUPABASE_URL}?select=*&order=id.desc&limit=1", headers=headers)
        dados = response.json()

        if dados:
            contexto_bruto = dados[0].get('contexto', 'Sem dados')
            print(f"📊 Analisando: {contexto_bruto}")

            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Resuma este log do NexoGenesis e defina a próxima prioridade: {contexto_bruto}"
            analise = model.generate_content(prompt)

            print(f"💡 INSIGHT: {analise.text}")
            
            payload = {"contexto": "Relatório de Inteligência 0856", "codigo_gerado": f"SUCESSO: {analise.text[:150]}"}
            requests.post(SUPABASE_URL, headers=headers, json=payload)
            print("✅ Inteligência guardada no Supabase.")
        else:
            print("💤 Sem dados novos.")
    except Exception as e:
        print(f"❌ Erro real na análise: {e}")

if __name__ == "__main__":
    agente_analista()
