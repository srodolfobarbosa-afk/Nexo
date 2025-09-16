import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class InternetSearchModule:
    """
    Módulo de busca na internet para o Nexo Gênesis
    Permite ao agente buscar informações, códigos e soluções online
    """
    
    def __init__(self):
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")
        self.google_cse_id = os.environ.get("GOOGLE_CSE_ID")
        self.search_history = []
    
    def search_web(self, query, num_results=5):
        """
        Busca informações na web usando Google Custom Search API
        """
        try:
            if self.google_api_key and self.google_cse_id:
                return self._google_search(query, num_results)
            else:
                # Fallback para DuckDuckGo (sem API key necessária)
                return self._duckduckgo_search(query, num_results)
        except Exception as e:
            print(f"Erro na busca web: {e}")
            return []
    
    def _google_search(self, query, num_results):
        """
        Busca usando Google Custom Search API
        """
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query,
            "num": num_results
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                    "source": "google"
                })
            
            self._log_search(query, results)
            return results
        else:
            raise Exception(f"Erro na API Google: {response.status_code}")
    
    def _duckduckgo_search(self, query, num_results):
        """
        Busca usando DuckDuckGo (fallback gratuito)
        """
        try:
            # Simulação de busca DuckDuckGo (implementação simplificada)
            # Em produção, usar biblioteca como duckduckgo-search
            url = f"https://duckduckgo.com/html/?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            search_results = soup.find_all('div', class_='result')[:num_results]
            
            for result in search_results:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "link": title_elem.get('href'),
                        "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                        "source": "duckduckgo"
                    })
            
            self._log_search(query, results)
            return results
            
        except Exception as e:
            print(f"Erro na busca DuckDuckGo: {e}")
            return []
    
    def scrape_content(self, url):
        """
        Extrai conteúdo de uma página web
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts e estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrai texto principal
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                "url": url,
                "content": text[:5000],  # Limita a 5000 caracteres
                "title": soup.title.string if soup.title else "",
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erro ao extrair conteúdo de {url}: {e}")
            return None
    
    def search_code_examples(self, technology, problem):
        """
        Busca exemplos de código específicos
        """
        query = f"{technology} {problem} example code github"
        results = self.search_web(query, 3)
        
        code_results = []
        for result in results:
            if any(site in result["link"] for site in ["github.com", "stackoverflow.com", "docs."]):
                content = self.scrape_content(result["link"])
                if content:
                    code_results.append({
                        **result,
                        "content": content["content"]
                    })
        
        return code_results
    
    def search_documentation(self, library_name):
        """
        Busca documentação oficial de bibliotecas
        """
        query = f"{library_name} official documentation"
        results = self.search_web(query, 3)
        
        doc_results = []
        for result in results:
            if any(keyword in result["link"] for keyword in ["docs.", "documentation", "readthedocs"]):
                content = self.scrape_content(result["link"])
                if content:
                    doc_results.append({
                        **result,
                        "content": content["content"]
                    })
        
        return doc_results
    
    def _log_search(self, query, results):
        """
        Registra histórico de buscas
        """
        search_log = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results_count": len(results),
            "results": results
        }
        self.search_history.append(search_log)
    
    def get_search_history(self):
        """
        Retorna histórico de buscas
        """
        return self.search_history

if __name__ == "__main__":
    # Teste do módulo
    search = InternetSearchModule()
    results = search.search_web("Python Flask API tutorial")
    print(f"Encontrados {len(results)} resultados")
    for result in results:
        print(f"- {result['title']}: {result['link']}")
