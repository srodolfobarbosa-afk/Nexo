import os
from dotenv import load_dotenv
from supabase import Client, create_client
import os
import logging
from dotenv import load_dotenv
from supabase import Client, create_client
from typing import Dict, List, Any
import time
import yfinance as yf  # Exemplo de API, pode ser substituída

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

logging.basicConfig(level=logging.INFO)


class MarketWatchAgent:
    """Agente simples para monitorar preços de ações e persistir em Supabase."""

    def __init__(self):
        try:
            if SUPABASE_URL and SUPABASE_KEY:
                self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
                logging.info("Conectado ao Supabase.")
            else:
                self.supabase = None
                logging.info("Supabase não configurado (variáveis de ambiente ausentes).")
        except Exception as e:
            logging.error(f"Erro ao conectar ao Supabase: {e}")
            self.supabase = None

        # Tenta inicializar utilitários internos, sem quebrar se faltarem
        try:
            from core.api_search import APISearch

            self.api_search = APISearch()
        except Exception:
            self.api_search = None

    def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Busca dados de um ticker usando yfinance (retorna dict simples)."""
        try:
            data = yf.download(ticker, period="1d")
            if data is None or data.empty:
                return {}
            return {
                "ticker": ticker,
                "close": float(data["Close"].iloc[-1]),
                "open": float(data["Open"].iloc[-1]),
                "high": float(data["High"].iloc[-1]),
                "low": float(data["Low"].iloc[-1]),
            }
        except Exception as e:
            logging.error(f"Erro ao buscar dados de {ticker}: {e}")
            return {}

    def detect_large_variation(self, previous_close: float, current_close: float, threshold: float = 0.05) -> bool:
        if previous_close == 0:
            return False
        variation = abs((current_close - previous_close) / previous_close)
        return variation > threshold

    def notify(self, message: str):
        """Placeholder para notificações; atualmente registra via logging."""
        logging.info(f"Notificação: {message}")

    def monitor_market(self, tickers: List[str], threshold: float = 0.05, interval: int = 60):
        try:
            previous_data: Dict[str, Dict[str, Any]] = {}
            while True:
                for ticker in tickers:
                    current_data = self.fetch_stock_data(ticker)
                    if current_data and "close" in current_data:
                        if ticker in previous_data:
                            prev_close = previous_data[ticker].get("close")
                            if prev_close is not None and self.detect_large_variation(prev_close, current_data["close"], threshold):
                                message = f"Grande variação detectada em {ticker}: {current_data['close']}"
                                self.notify(message)
                        previous_data[ticker] = current_data
                    else:
                        logging.warning(f"Dados insuficientes para {ticker}")

                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Monitoramento encerrado pelo usuário.")
        except Exception as e:
            logging.error(f"Erro no monitoramento: {e}")

    def persist_data(self, data: Dict[str, Any]):
        try:
            if not self.supabase:
                logging.warning("Supabase não configurado. Ignorando persistência.")
                return
            response = self.supabase.table("market_data").insert(data).execute()
            if getattr(response, "error", None):
                logging.error(f"Erro ao persistir dados no Supabase: {response.error}")
        except Exception as e:
            logging.error(f"Erro ao persistir dados: {e}")

    def run(self, tickers: List[str]):
        try:
            self.monitor_market(tickers)
        except Exception as e:
            logging.error(f"Erro na execução do agente: {e}")


if __name__ == "__main__":
    agent = MarketWatchAgent()
    tickers = ["AAPL", "MSFT", "GOOG"]  # Exemplo de tickers
    agent.run(tickers)
