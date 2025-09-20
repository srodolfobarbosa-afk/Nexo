"""
Módulo utilitário para busca inteligente em APIs externas.
Suporta Google, Gemini, OpenAI, APIs financeiras, Supabase, etc.
Pode ser expandido para qualquer fonte externa.
"""
import os
import requests
import google.generativeai as genai

class APISearch:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)

    def search_google(self, query):
        # Exemplo: usar Google Custom Search API
        api_key = os.getenv("GOOGLE_API_KEY")
        cx = os.getenv("GOOGLE_CSE_ID")
        if not api_key or not cx:
            return "Google API Key ou CSE ID não configurados."
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
        return f"Erro Google Search: {resp.text}"

    def search_gemini(self, prompt):
        if not self.gemini_api_key:
            return "GEMINI_API_KEY não configurada."
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text

    def search_openai(self, prompt):
        if not self.openai_api_key:
            return "OPENAI_API_KEY não configurada."
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}
        payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Erro OpenAI: {resp.text}"

    def search_supabase(self, table, query):
        # Exemplo básico usando REST API do Supabase
        if not self.supabase_url or not self.supabase_key:
            return "SUPABASE_URL ou SUPABASE_KEY não configurados."
        url = f"{self.supabase_url}/rest/v1/{table}?{query}"
        headers = {"apikey": self.supabase_key, "Authorization": f"Bearer {self.supabase_key}"}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        return f"Erro Supabase: {resp.text}"

    def search_finance(self, symbol):
        # Exemplo: buscar cotação via API pública
        url = f"https://api.hgbrasil.com/finance/stock_price?key=demo&symbol={symbol}"
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
        return f"Erro Finance API: {resp.text}"

    # Adicione outros métodos conforme necessário
