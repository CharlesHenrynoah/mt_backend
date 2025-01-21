import asyncio
from user_agent import UserAgent
from url_agent import URLProcessorAgent
from scraper_agent import ScraperAgent
from config import (
    USER_AGENT_JID,
    URL_AGENT_JID,
    SCRAPER_AGENT_JID,
    AGENT_PASSWORD
)

async def main():
    try:
        # Créer et démarrer les agents
        user_agent = UserAgent(USER_AGENT_JID, AGENT_PASSWORD)
        url_agent = URLProcessorAgent(URL_AGENT_JID, AGENT_PASSWORD)
        scraper_agent = ScraperAgent(SCRAPER_AGENT_JID, AGENT_PASSWORD)
        
        print("Démarrage des agents...")
        
        await user_agent.start()
        await url_agent.start()
        await scraper_agent.start()
        
        print("Tous les agents sont démarrés et prêts !")
        print("\nVous pouvez maintenant entrer vos requêtes.")
        print("Exemple: 'Je cherche un développeur en Inde à moins de 50 euros'")
        print("Tapez 'quit' pour quitter.")
        
        # Attendre que l'utilisateur veuille quitter
        while user_agent.is_alive():
            await asyncio.sleep(1)
        
    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")
    
    finally:
        # Arrêter tous les agents
        await user_agent.stop()
        await url_agent.stop()
        await scraper_agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
