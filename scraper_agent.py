import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import aiohttp
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
from config import GEMINI_API_KEY, SCRAPER_AGENT_JID, AGENT_PASSWORD

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

class ScraperAgent(Agent):
    class ScrapeWebsites(CyclicBehaviour):
        async def scrape_url(self, url):
            try:
                # En-têtes pour simuler un navigateur web
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=30) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extraire les informations pertinentes
                            title = soup.title.string if soup.title else "No title"
                            
                            # Extraire les informations des développeurs
                            dev_cards = soup.find_all('div', {'class': ['seller-card', 'gig-card']})
                            dev_info = []
                            
                            for card in dev_cards[:5]:  # Limiter à 5 développeurs pour éviter trop de données
                                name = card.find('a', {'class': 'seller-name'})
                                price = card.find('span', {'class': 'price'})
                                rating = card.find('span', {'class': 'rating'})
                                
                                dev_info.append({
                                    'name': name.text if name else 'Non spécifié',
                                    'price': price.text if price else 'Non spécifié',
                                    'rating': rating.text if rating else 'Non spécifié'
                                })
                            
                            # Utiliser Gemini pour résumer le contenu
                            prompt = f"""
                            Résumez les informations des développeurs trouvés sur Fiverr:
                            Titre de la page: {title}
                            
                            Développeurs trouvés:
                            {json.dumps(dev_info, indent=2, ensure_ascii=False)}
                            
                            Donnez un résumé concis en français des développeurs disponibles, leurs tarifs et leurs évaluations.
                            Mentionnez également si les développeurs correspondent aux critères de recherche (pays/langue, budget).
                            """
                            
                            response = model.generate_content(prompt)
                            return response.text
                        else:
                            return f"Erreur lors de l'accès à {url}: {response.status} - Accès refusé par Fiverr"
            except Exception as e:
                return f"Erreur lors du scraping de {url}: {str(e)}"

        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                urls = msg.body.split('\n')
                results = []
                
                for url in urls:
                    print(f"Scraping de l'URL: {url}")
                    summary = await self.scrape_url(url.strip())
                    results.append(f"URL: {url}\nRésumé: {summary}\n")
                
                # Send results back to the user agent
                response = Message(to=str(msg.sender))
                response.body = "\n".join(results)
                response.set_metadata("performative", "inform")
                await self.send(response)

    async def setup(self):
        print("Agent Scraper démarré")
        behaviour = self.ScrapeWebsites()
        self.add_behaviour(behaviour)

if __name__ == "__main__":
    scraper_agent = ScraperAgent(SCRAPER_AGENT_JID, AGENT_PASSWORD)
    scraper_agent.start()
