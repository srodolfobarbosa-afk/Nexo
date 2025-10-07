import asyncio
import logging
from typing import Any, Dict

import yfinance as yf
from supabase import Client, create_client

logging.basicConfig(level=logging.INFO)

SUPABASE_URL = None
SUPABASE_KEY = None


class MarketWatcherEconomico:
    def __init__(
        self, supabase_url: str | None = None, supabase_key: str | None = None
    ):
        self.supabase: Client | None = None
        if supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
                logging.info("Conectado ao Supabase.")
            except Exception as e:
                logging.error(f"Erro ao conectar ao Supabase: {e}")
                self.supabase = None
        self.data_sources = {"yfinance": yf}

    async def connect_to_database(self):
        # Apenas placeholder; função assíncrona caso a biblioteca supabase seja usada em modo async
        logging.info("MarketWatcherEconomico: connect_to_database (placeholder)")

    async def fetch_market_data(
        self, symbol: str, source: str = "yfinance"
    ) -> Dict[str, Any]:
        try:
            if source not in self.data_sources:
                raise ValueError(f"Fonte de dados '{source}' não disponível.")
            api = self.data_sources[source]
            ticker = api.Ticker(symbol)
            data = ticker.history(period="1d")
            if data is None or data.empty:
                return {}
            return {
                "Close": data["Close"],
                "Open": data["Open"],
                "High": data["High"],
                "Low": data["Low"],
            }
        except Exception as e:
            logging.error(f"Erro ao buscar dados de mercado: {e}")
            return {}

    async def analyze_market_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not data:
                return {"analysis": "Dados insuficientes"}
            # Extrai último preço de fechamento com segurança
            close_series = data.get("Close")
            if hasattr(close_series, "iloc"):
                close_price = float(close_series.iloc[-1])
            else:
                # se for dict-like
                try:
                    close_price = float(list(close_series)[-1])
                except Exception:
                    return {"analysis": "Dados insuficientes"}

            analysis = {
                "close_price": close_price,
                "recommendation": "Compra" if close_price < 100 else "Venda",
            }
            return analysis
        except Exception as e:
            logging.error(f"Erro na análise de dados de mercado: {e}")
            return {"analysis": "Erro na análise"}

    async def store_data(self, data: Dict[str, Any], symbol: str) -> None:
        try:
            if not self.supabase:
                logging.warning("Supabase não configurado. Ignorando persistência.")
                return
            await (
                self.supabase.table("market_data")
                .insert({"symbol": symbol, "data": data})
                .execute()
            )
        except Exception as e:
            logging.error(f"Erro ao armazenar dados no Supabase: {e}")

    async def send_alerts(self, alert_message: str) -> None:
        logging.warning(f"Alerta: {alert_message}")

    async def run(self):
        await self.connect_to_database()
        while True:
            try:
                market_data = await self.fetch_market_data("AAPL")
                analysis = await self.analyze_market_data(market_data)
                await self.store_data(analysis, "AAPL")

                if analysis.get("recommendation") == "Compra":
                    await self.send_alerts("Oportunidade de compra identificada!")
                await asyncio.sleep(60)
            except Exception as e:
                logging.error(f"Erro durante a execução do agente: {e}")
                await asyncio.sleep(60)


async def main():
    agent = MarketWatcherEconomico(SUPABASE_URL, SUPABASE_KEY)
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
