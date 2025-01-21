import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import google.generativeai as genai
import csv
import os
import json
from config import GEMINI_API_KEY, URL_AGENT_JID, SCRAPER_AGENT_JID, AGENT_PASSWORD

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

class URLProcessorAgent(Agent):
    class ProcessQuery(CyclicBehaviour):
        def __init__(self):
            super().__init__()
            self.url_mapping = self._load_url_mapping()
            self.language_mapping = {
                "hindi": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=seller_language%3Ahi",
                "bengali": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=seller_language%3Abn",
                "inde": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=seller_language%3Ahi"
            }
            self.budget_mapping = {
                "50": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=price%3A50",
                "moins cher": "https://fr.fiverr.com/categories/programming-tech/website-development?source=drop_down_filters&filter=auto&ref=price%3A50"
            }

        def _load_url_mapping(self):
            mapping = {}
            try:
                csv_path = os.path.join(os.path.dirname(__file__), 
                                      "Plateformes de freelances - Fiver - Développement de sites web filtres.csv")
                
                with open(csv_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)  # Skip header
                    for row in reader:
                        if len(row) >= 2:
                            category = row[0].strip()
                            url = row[1].strip()
                            if url:  # Only add if URL exists
                                mapping[category.lower()] = url
            except Exception as e:
                print(f"Erreur lors du chargement du fichier CSV: {str(e)}")
            return mapping

        async def analyze_query(self, query):
            prompt = f"""
            Analysez cette requête: "{query}"
            et identifiez:
            1. Le pays ou la langue du développeur (cherchez spécifiquement: Inde, Hindi, Bengali)
            2. Le budget (cherchez spécifiquement les montants en euros)
            3. Les catégories de site web ou compétences recherchées
            
            Répondez EXACTEMENT dans ce format JSON:
            {{
                "pays_langue": "Inde ou Hindi ou Bengali ou None si non trouvé",
                "budget": "montant en euros ou None si non trouvé",
                "categories": ["catégorie1", "catégorie2"]
            }}
            """
            
            response = model.generate_content(prompt)
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            try:
                clean_response = clean_response.replace('null', 'None').replace('"None"', 'None')
                return eval(clean_response)
            except Exception as e:
                print(f"Erreur lors du parsing de la réponse: {str(e)}")
                return {"pays_langue": None, "budget": None, "categories": []}

        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    user_query = msg.body
                    print(f"Agent URL: Traitement de la requête: {user_query}")

                    # Analyse de la requête
                    analysis = await self.analyze_query(user_query)
                    print(f"Analyse: {json.dumps(analysis, indent=2, ensure_ascii=False)}")

                    # Collecter les URLs
                    urls = set()

                    # Ajouter l'URL pour la langue/pays
                    if analysis["pays_langue"]:
                        pays_langue = analysis["pays_langue"].lower()
                        if pays_langue in self.language_mapping:
                            urls.add(self.language_mapping[pays_langue])

                    # Ajouter l'URL pour le budget
                    if analysis["budget"]:
                        budget = analysis["budget"]
                        if budget in self.budget_mapping:
                            urls.add(self.budget_mapping[budget])

                    # Ajouter les URLs des catégories
                    for category in analysis.get("categories", []):
                        if category.lower() in self.url_mapping:
                            urls.add(self.url_mapping[category.lower()])

                    if urls:
                        # Send URLs to scraper agent
                        msg = Message(to=SCRAPER_AGENT_JID)
                        msg.body = '\n'.join(urls)
                        msg.set_metadata("performative", "request")
                        await self.send(msg)
                        print(f"Agent URL: {len(urls)} URLs envoyées au scraper")
                    else:
                        # Send "no results" message back to user agent
                        msg = Message(to=str(msg.sender))
                        msg.body = "Aucune URL correspondante trouvée pour vos critères."
                        msg.set_metadata("performative", "inform")
                        await self.send(msg)

                except Exception as e:
                    print(f"Agent URL: Erreur lors du traitement: {str(e)}")
                    msg = Message(to=str(msg.sender))
                    msg.body = f"Une erreur s'est produite: {str(e)}"
                    msg.set_metadata("performative", "inform")
                    await self.send(msg)

    async def setup(self):
        print("Agent Processeur d'URL démarré")
        behaviour = self.ProcessQuery()
        self.add_behaviour(behaviour)

if __name__ == "__main__":
    url_agent = URLProcessorAgent(URL_AGENT_JID, AGENT_PASSWORD)
    url_agent.start()
