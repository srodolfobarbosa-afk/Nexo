import requests
import time
import os

# Dados essenciais
SUPABASE_URL = "https://jyfurrvkqrdkwtvtfzbw.supabase.co/rest/v1/nexo_memoria"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5ZnVycnZrcXJka3d0dnRmemJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5MTYzMjAsImV4cCI6MjA3MzQ5MjMyMH0.zuTYPgiy4PbsGdkG_rDX-YREhWcy225U2732Lq__Pno"

def bater_coracao():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    while True:
        try:
            print("💓 NEXO: Estou vivo. Enviando sinal...")
            payload = {"contexto": "Sinal de Vida", "codigo_gerado": "ESTADO: ONLINE"}
            r = requests.post(SUPABASE_URL, headers=headers, json=payload, timeout=10)
            
            if r.status_code == 201:
                print("✅ Sinal recebido pelo Supabase.")
            else:
                print(f"⚠️ Supabase respondeu com erro: {r.status_code}")
                
            time.sleep(60) # Espera 1 minuto para a próxima batida
            
        except Exception as e:
            print(f"🚑 ERRO DETECTADO: {e}. Reiniciando sistema em 10s...")
            time.sleep(10)
            # O sistema tenta se relançar sozinho
            os.system("python agente_0856.py")

if __name__ == "__main__":
    bater_coracao()
