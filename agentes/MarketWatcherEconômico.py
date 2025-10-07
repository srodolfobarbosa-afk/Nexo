from .MarketWatcherEconomico import MarketWatcherEconomico

"""
Compat shim: alguns módulos importavam o arquivo com acento (MarketWatcherEconômico).
Este arquivo apenas reexporta a versão sem acento para manter compatibilidade.
"""

__all__ = ["MarketWatcherEconomico"]
import asyncio
import time
from typing import Any, Dict, List

import yfinance as yf  # Exemplo de API, substituir conforme necessidade
from supabase import Client, create_client

from .MarketWatcherEconomico import MarketWatcherEconomico

__all__ = ["MarketWatcherEconomico"]
