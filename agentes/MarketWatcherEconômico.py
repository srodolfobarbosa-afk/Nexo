```python
import time
import asyncio
from supabase import Client, create_client
from typing import Dict, List, Any
import yfinance as yf #Exemplo de API, substituir conforme necessidade

# Substituir com suas credenciais
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"

class MarketWatcherEconomico:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.data_sources = {'yfinance':yf} #Exemplo, adicionar outras APIs

    async def connect_to_database(self):
        try:
            await self.supabase.auth.set_auth("YOUR_AUTH_TOKEN") # Substituir com a sua autenticação
            print("Conectado ao Supabase!")
        except Exception as e:
            print(f"Erro ao conectar ao Supabase: {e}")

    async def fetch_market_data(self, symbol: str, source: str ="yfinance") -> Dict[str, Any]:
        try:
            if source not in self.data_sources:
                raise ValueError(f"Fonte de dados '{source}' não disponível.")
            api = self.data_sources[source]
            ticker = api.Ticker(symbol)
            data = ticker.history(period="1d")
            return data.to_dict()
        except Exception as e:
            print(f"Erro ao buscar dados de mercado: {e}")
            return {}

    async def analyze_market_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementar algoritmos de análise técnica e fundamentalista aqui. 
        # Este é um exemplo simplificado, precisa ser expandido
        try:
            if not data:
                return {"analysis": "Dados insuficientes"}
            close_price = data['Close'].iloc[-1]
            analysis = {"close_price": close_price, "recommendation": "Compra" if close_price < 100 else "Venda"}
            return analysis
        except Exception as e:
            print(f"Erro na análise de dados de mercado: {e}")
            return {"analysis": "Erro na análise"}

    async def store_data(self, data: Dict[str, Any], symbol:str) -> None:
        try:
            await self.supabase.table('market_data').insert({'symbol':symbol, 'data':data}).execute()
        except Exception as e:
            print(f"Erro ao armazenar dados no Supabase: {e}")

    async def send_alerts(self, alert_message: str) -> None:
        # Implementar sistema de alertas (email, notificações push, etc)
        print(f"Alerta: {alert_message}")

    async def run(self):
        await self.connect_to_database()
        while True:
            try:
                # Substitua AAPL pelo ticker desejado
                market_data = await self.fetch_market_data("AAPL")
                analysis = await self.analyze_market_data(market_data)
                await self.store_data(analysis, "AAPL")

                if analysis['recommendation'] == 'Compra':
                    await self.send_alerts("Oportunidade de compra identificada!")
                time.sleep(60) #Ajustar o intervalo de tempo
            except Exception as e:
                print(f"Erro durante a execução do agente: {e}")
                time.sleep(60)


async def main():
    agent = MarketWatcherEconomico()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())

```
