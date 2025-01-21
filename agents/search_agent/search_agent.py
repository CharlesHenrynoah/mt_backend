from ..core.base_agent import BaseAgent
from ..core.message_types import MessageType
import google.generativeai as genai
import aiohttp
from bs4 import BeautifulSoup
import json

class SearchAgent(BaseAgent):
    """Agent responsable de la recherche et du scraping"""
    
    def __init__(self, jid, password, gemini_api_key):
        super().__init__(jid, password)
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    class SearchBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.get_metadata("type") == MessageType.SEARCH_REQUEST.value:
                try:
                    query = msg.body
                    results = await self.agent.process_search(query)
                    
                    # Envoyer les résultats
                    response = Message(to=str(msg.sender))
                    response.body = json.dumps(results)
                    response.set_metadata("type", MessageType.SEARCH_RESPONSE.value)
                    await self.send(response)
                    
                except Exception as e:
                    error_msg = Message(to=str(msg.sender))
                    error_msg.body = str(e)
                    error_msg.set_metadata("type", MessageType.ERROR.value)
                    await self.send(error_msg)
    
    async def process_search(self, query):
        """Traite une requête de recherche"""
        # Analyser la requête avec Gemini
        analysis = await self.analyze_query(query)
        
        # Collecter les URLs pertinentes
        urls = await self.get_relevant_urls(analysis)
        
        # Scraper les résultats
        results = await self.scrape_urls(urls)
        
        return results
    
    async def analyze_query(self, query):
        """Analyse la requête utilisateur avec Gemini"""
        prompt = f"""
        Analysez cette requête: "{query}"
        et identifiez:
        1. Le pays ou la langue du développeur
        2. Le budget
        3. Les compétences recherchées
        
        Répondez au format JSON.
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
    
    async def get_relevant_urls(self, analysis):
        """Obtient les URLs pertinentes basées sur l'analyse"""
        # Implémenter la logique de mapping des critères aux URLs
        return []
    
    async def scrape_urls(self, urls):
        """Scrape les URLs et extrait les informations pertinentes"""
        results = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            # Extraire les informations pertinentes
                            # Ajouter la logique de scraping spécifique ici
                            results.append({
                                "url": url,
                                "title": soup.title.string if soup.title else "No title",
                                "data": {}  # Ajouter les données scrapées
                            })
                except Exception as e:
                    self.logger.error(f"Erreur lors du scraping de {url}: {str(e)}")
        
        return results
    
    async def setup(self):
        await super().setup()
        self.add_cyclic_behaviour(self.SearchBehaviour)
