import asyncio
from playwright.async_api import async_playwright
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebAgent:
    """
    Um agente para navegação e extração de dados da web usando Playwright.
    """

    async def search_and_extract(self, query: str, num_results: int = 3):
        """
        Realiza uma pesquisa no Google e extrai o conteúdo dos primeiros resultados.
        """
        results = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                logger.info(f"Navegando para o Google para pesquisar: {query}")
                await page.goto("https://www.google.com")
                await page.fill('textarea[name="q"]', query)
                await page.press('textarea[name="q"]', 'Enter')
                
                await page.wait_for_selector('div.g', timeout=10000)
                
                logger.info("Resultados encontrados. Extraindo dados...")
                search_results = await page.locator('div.g').all()
                
                for i, result in enumerate(search_results[:num_results]):
                    try:
                        title = await result.locator('h3').inner_text()
                        url = await result.locator('a').first.get_attribute('href')
                        
                        await page.goto(url, timeout=10000)
                        content = await page.inner_text('body')
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "content": content[:1000]
                        })
                        logger.info(f"Extração bem-sucedida do resultado {i+1}: {title}")
                    except Exception as e:
                        logger.warning(f"Erro ao extrair o conteúdo do resultado: {e}")
                        continue
                
                await browser.close()
                return results

        except Exception as e:
            logger.error(f"Erro geral na navegação web: {e}")
            return []

    async def get_page_content(self, url: str):
        """
        Navega para uma URL específica e retorna o conteúdo da página.
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=10000)
                content = await page.inner_text('body')
                await browser.close()
                return content
        except Exception as e:
            logger.error(f"Erro ao obter conteúdo da página {url}: {e}")
            return ""

# Exemplo de uso (para testes)
async def main():
    agent = WebAgent()
    query = "o que é inteligência artificial geral"
    results = await agent.search_and_extract(query)
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
