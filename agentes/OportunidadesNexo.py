import logging
import os
from typing import Any, Dict

import pandas as pd
from supabase import Client, create_client

logging.basicConfig(level=logging.INFO)


class OportunidadesNexo:
    """Classe para identificar oportunidades usando dados do Nexo via Supabase."""

    def __init__(
        self, supabase_url: str | None = None, supabase_key: str | None = None
    ):
        if supabase_url is None:
            supabase_url = os.environ.get("SUPABASE_URL")
        if supabase_key is None:
            supabase_key = os.environ.get("SUPABASE_KEY")

        self.supabase: Client | None = None
        if supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
                logging.info("Conectado ao Supabase.")
            except Exception as e:
                logging.error(f"Erro ao conectar ao Supabase: {e}")
                self.supabase = None
        else:
            logging.warning(
                "SUPABASE_URL ou SUPABASE_KEY ausentes; funcionalidade limitada."
            )

        try:
            from core.api_search import APISearch

            self.api_search = APISearch()
        except Exception:
            self.api_search = None

        self.data: pd.DataFrame | None = None

    def coletar_dados_nexo(self, table: str = "nome_da_sua_tabela") -> pd.DataFrame:
        try:
            if not self.supabase:
                logging.warning("Supabase não configurado; retornando DataFrame vazio.")
                return pd.DataFrame()
            response = self.supabase.table(table).select("*").execute()
            if getattr(response, "data", None):
                self.data = pd.DataFrame(response.data)
                return self.data
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"Erro ao coletar dados do Nexo: {e}")
            return pd.DataFrame()

    def analisar_dados_mercado(self, dados: pd.DataFrame) -> Dict[str, Any]:
        try:
            if dados is None or dados.empty:
                return {"tendencia": "indefinida", "potencial": 0.0}
            return {"tendencia": "crescimento", "potencial": 0.8}
        except Exception as e:
            logging.error(f"Erro na análise de dados de mercado: {e}")
            return {}

    def prever_tendencias(self, dados: pd.DataFrame) -> Dict[str, Any]:
        try:
            return {"previsao_receita": 1000000, "previsao_inovacao": 0.9}
        except Exception as e:
            logging.error(f"Erro na previsão de tendências: {e}")
            return {}

    def gerar_relatorio(self, resultados: Dict[str, Any]) -> str:
        try:
            relatorio = "Relatório de Oportunidades:\n\n"
            relatorio += f"Tendência de Mercado: {resultados.get('tendencia', 'N/A')}\n"
            relatorio += f"Potencial de Mercado: {resultados.get('potencial', 'N/A')}\n"
            relatorio += (
                f"Previsão de Receita: {resultados.get('previsao_receita', 'N/A')}\n"
            )
            relatorio += (
                f"Previsão de Inovação: {resultados.get('previsao_inovacao', 'N/A')}\n"
            )
            return relatorio
        except Exception as e:
            logging.error(f"Erro na geração de relatório: {e}")
            return "Erro na geração do relatório."

    def executar(self, query: str):
        self.coletar_dados_nexo()
        dados = self.data
        if dados is not None and not dados.empty:
            analise = self.analisar_dados_mercado(dados)
            previsao = self.prever_tendencias(dados)
            relatorio = self.gerar_relatorio({**analise, **previsao})
            logging.info(relatorio)
        else:
            logging.warning("Nenhum dado encontrado.")
            previsao = self.prever_tendencias(dados)
