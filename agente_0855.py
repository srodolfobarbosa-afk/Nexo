import requests
import datetime
import time

# DNA de Conexão
SUPABASE_URL = "https://jyfurrvkqrdkwtvtfzbw.supabase.co/rest/v1/nexo_memoria"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5ZnVycnZrcXJka3d0dnRmemJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5MTYzMjAsImV4cCI6MjA3MzQ5MjMyMH0.zuTYPgiy4PbsGdkG_rDX-YREhWcy225U2732Lq__Pno"

def agente_watcher():
    print("🤖 AGENTE 0855: Iniciando monitoramento de eventos...")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Simulação de coleta de evento crítico
    evento = {
        "contexto": f"Monitoramento Agente 0855 - {datetime.datetime.now()}",
        "codigo_gerado": "STATUS: SISTEMA OPERALIONAL 100% - AGENTE ATIVO"
    }
    
    try:
        r = requests.post(SUPABASE_URL, headers=headers, json=evento)
        if r.status_code in [200, 201]:
            print("✅ EVENTO CAPTURADO E ENVIADO PARA A NUVEM!")
        else:
            print(f"⚠️ Falha no envio: {r.status_code}")
    except Exception as e:
        print(f"❌ Erro de rede: {e}")

if __name__ == "__main__":
    agente_watcher()
