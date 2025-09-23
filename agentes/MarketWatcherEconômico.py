from .MarketWatcherEconomico import MarketWatcherEconomico

"""
Compat shim: alguns módulos importavam o arquivo com acento (MarketWatcherEconômico).
Este arquivo apenas reexporta a versão sem acento para manter compatibilidade.
"""

__all__ = ["MarketWatcherEconomico"]
import time
import asyncio
from supabase import Client, create_client
from typing import Dict, List, Any
import yfinance as yf #Exemplo de API, substituir conforme necessidade
import time
import asyncio
from supabase import Client, create_client
from typing import Dict, List, Any
import yfinance as yf #Exemplo de API, substituir conforme necessidade

from .MarketWatcherEconomico import MarketWatcherEconomico

__all__ = ["MarketWatcherEconomico"]

