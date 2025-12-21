import os
import google.generativeai as genai
import requests

GEMINI_KEY = "AIzaSyDrbRaS9jRRczo5gs6tMwfeR88LofOLHqE"
SUPABASE_URL = "https://jyfurrvkqrdkwtvtfzbw.supabase.co/rest/v1/nexo_memoria"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5ZnVycnZrcXJka3d0dnRmemJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5MTYzMjAsImV4cCI6MjA3MzQ5MjMyMH0.zuTYPgiy4PbsGdkG_rDX-YREhWcy225U2732Lq__Pno"

def sincronizar_nexo():
    try:
        print("🚀 NEXOGENESIS: Conectando ao Gemini 2.5 Flash...")
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = "Analise o projeto NexoGenesis. Dê uma ordem de ativação para o agente_0855.py e explique como o Supabase ajudará na persistência."
        resposta = model.generate_content(prompt)
        
        print(f"\n[DIRETRIZ DO LÍDER]:\n{resposta.text}")
        
        # Teste de persistência no Supabase
        headers = {
            "apikey": SUPABASE_KEY, 
            "Authorization": f"Bearer {SUPABASE_KEY}", 
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        payload = {"contexto": "Ativação Real", "codigo_gerado": "v4.0 Híbrida"}
        r = requests.post(SUPABASE_URL, headers=headers, json=payload)
        
        if r.status_code in [200, 201]:
            print("\n✅ PERSISTÊNCIA ATIVA: Gravado no Supabase com sucesso!")
        else:
            print(f"\n⚠️ Erro na persistência: {r.status_code}")

    except Exception as e:
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    sincronizar_nexo()
