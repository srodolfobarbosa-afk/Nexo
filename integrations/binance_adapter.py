import os
import logging
from typing import Dict, Any

logger = logging.getLogger("binance_adapter")


def is_live_trading_enabled() -> bool:
    return os.environ.get("BINANCE_LIVE", "0") in ("1", "true", "True")


def place_order(symbol: str, side: str, quantity: float, price: float = None) -> Dict[str, Any]:
    """Place order in paper mode by default. Use BINANCE_API_KEY and BINANCE_API_SECRET for live mode."""
    if not is_live_trading_enabled():
        logger.info("Paper trade: simulated order placed")
        return {"status": "paper", "symbol": symbol, "side": side, "quantity": quantity, "price": price}
    # live mode (placeholder - integrate with python-binance or ccxt)
    api_key = os.environ.get("BINANCE_API_KEY")
    api_secret = os.environ.get("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise RuntimeError("BINANCE_API_KEY/SECRET not configured for live trading")
    # Lazy import of real SDK optional
    try:
        from binance.client import Client

        client = Client(api_key, api_secret, testnet=not is_live_trading_enabled())
        order = client.create_order(symbol=symbol, side=side, type="MARKET", quantity=quantity)
        return order
    except Exception as e:
        logger.exception("Binance order failed")
        return {"error": str(e)}
