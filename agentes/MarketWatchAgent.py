```python
import os
from dotenv import load_dotenv
from supabase import Client, create_client
from typing import Dict, List, Any
import time
import yfinance as yf #Exemplo de API, pode ser substituída

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class MarketWatchAgent:
    def __init__(self):
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("Conectado ao Supabase.")
        except Exception as e:
            print(f"Erro ao conectar ao Supabase: {e}")
        from core.api_search import APISearch
        self.api_search = APISearch()
            exit(1)

    def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        try:
            data = yf.download(ticker, period="1d") #Baixa dados de 1 dia
            if data.empty:
                return {}
            return {
                "ticker": ticker,
                "close": data["Close"][-1],
                "open": data["Open"][-1],
                "high": data["High"][-1],
                "low": data["Low"][-1],
            }
        except Exception as e:
            print(f"Erro ao buscar dados de {ticker}: {e}")
            return {}

    def detect_large_variation(self, previous_close: float, current_close: float, threshold: float = 0.05) -> bool:
        variation = abs((current_close - previous_close) / previous_close)
        return variation > threshold

    def notify(self, message: str):
        # Substitua pela sua implementação de notificação (email, SMS, etc)
        print(f"Notificação: {message}")

    def monitor_market(self, tickers: List[str], threshold: float = 0.05, interval: int = 60):
        try:
            previous_data = {}
            while True:
                for ticker in tickers:
                    current_data = self.fetch_stock_data(ticker)
                    if current_data and "close" in current_data:
                        if ticker in previous_data:
                            if self.detect_large_variation(previous_data[ticker]["close"], current_data["close"], threshold):
                                message = f"Grande variação detectada em {ticker}: {current_data['close']}"
                                self.notify(message)
                        previous_data[ticker] = current_data
                    else:
                        print(f"Dados insuficientes para {ticker}")

                time.sleep(interval)
        except KeyboardInterrupt:
            print("Monitoramento encerrado.")
        except Exception as e:
            print(f"Erro no monitoramento: {e}")


    def persist_data(self, data: Dict[str, Any]):
        try:
            response = self.supabase.table("market_data").insert(data).execute()
            if response.error:
                print(f"Erro ao persistir dados no Supabase: {response.error}")

        except Exception as e:
            print(f"Erro ao persistir dados: {e}")

    def run(self, tickers:List[str]):
        try:
            self.monitor_market(tickers)
        except Exception as e:
            print(f"Erro na execução do agente: {e}")


if __name__ == "__main__":
    agent = MarketWatchAgent()
    tickers = ["AAPL", "MSFT", "GOOG"] #Exemplo de tickers
    agent.run(tickers)
```
