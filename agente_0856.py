import os
import time

import requests

# Dados essenciais
SUPABASE_URL = "https://jyfurrvkqrdkwtvtfzbw.supabase.co/rest/v1/nexo_memoria"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp5ZnVycnZrcXJka3d0dnRmemJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5MTYzMjAsImV4cCI6MjA3MzQ5MjMyMH0.zuTYPgiy4PbsGdkG_rDX-YREhWcy225U2732Lq__Pno"


def agente_analista():
    """Executa uma análise e publica o estado atual do sistema."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    try:
        print("🧠 NEXO: Analisando ciclo e enviando diagnóstico...")
        payload = {
            "contexto": "Diagnóstico de operação do ciclo NEXO",
            "codigo_gerado": "STATUS: ANALISE ATIVA - SISTEMA ONLINE",
        }
        r = requests.post(SUPABASE_URL, headers=headers, json=payload, timeout=10)

        if r.status_code in [200, 201]:
            print("✅ Diagnóstico enviado ao Supabase.")
        else:
            print(f"⚠️ Supabase respondeu com erro: {r.status_code} - {r.text[:180]}")
        return r.status_code
    except Exception as e:
        print(f"🚑 ERRO DETECTADO: {e}")
        return None


def bater_coracao():
    """Modo standalone: mantém o agente vivo e emitindo pulsos."""
    while True:
        try:
            agente_analista()
            print("💓 NEXO: aguardando próximo pulso em 60s...")
            time.sleep(60)
        except Exception as e:
            print(f"🚑 Falha do agente: {e}. Reiniciando em 10s...")
            time.sleep(10)
            os.system("python agente_0856.py")


if __name__ == "__main__":
    bater_coracao()
