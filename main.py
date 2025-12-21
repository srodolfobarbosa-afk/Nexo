import time
from agente_0855 import agente_watcher
from agente_0856 import agente_analista

if __name__ == "__main__":
    print("🚀 NEXOGENESIS V2 - SISTEMA MULTI-AGENTE ONLINE")
    while True:
        agente_watcher()  # Coleta
        time.sleep(10)    # Espera 10 segundos para o dado assentar
        agente_analista() # Analisa
        
        print("💤 Ciclo completo. Aguardando 1 hora...")
        time.sleep(3600)
