import asyncio
from spade import quit_spade
from agents.auth_agent.auth_agent import AuthAgent
from agents.search_agent.search_agent import SearchAgent
from agents.data_agent.data_agent import DataAgent
from agents.external_agent.external_agent import ExternalAgent
from config import (
    USER_AGENT_JID,
    AUTH_AGENT_JID,
    SEARCH_AGENT_JID,
    DATA_AGENT_JID,
    EXTERNAL_AGENT_JID,
    AGENT_PASSWORD,
    GEMINI_API_KEY,
    JWT_SECRET_KEY
)
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Créer les agents
        auth_agent = AuthAgent(AUTH_AGENT_JID, AGENT_PASSWORD, JWT_SECRET_KEY)
        search_agent = SearchAgent(SEARCH_AGENT_JID, AGENT_PASSWORD, GEMINI_API_KEY)
        data_agent = DataAgent(DATA_AGENT_JID, AGENT_PASSWORD)
        external_agent = ExternalAgent(EXTERNAL_AGENT_JID, AGENT_PASSWORD)
        
        # Démarrer les agents
        logger.info("Démarrage des agents...")
        
        await auth_agent.start()
        logger.info("Agent d'authentification démarré")
        
        await search_agent.start()
        logger.info("Agent de recherche démarré")
        
        await data_agent.start()
        logger.info("Agent de données démarré")
        
        await external_agent.start()
        logger.info("Agent externe démarré")
        
        logger.info("Tous les agents sont démarrés et prêts !")
        logger.info("\nUtilisez l'API REST pour interagir avec le système.")
        logger.info("Documentation de l'API disponible sur: http://localhost:8000/docs")
        
        # Garder le programme en vie
        while all([
            auth_agent.is_alive(),
            search_agent.is_alive(),
            data_agent.is_alive(),
            external_agent.is_alive()
        ]):
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur...")
    except Exception as e:
        logger.error(f"Une erreur s'est produite: {str(e)}")
    finally:
        # Arrêter tous les agents
        logger.info("Arrêt des agents...")
        await auth_agent.stop()
        await search_agent.stop()
        await data_agent.stop()
        await external_agent.stop()
        await quit_spade()
        logger.info("Système arrêté.")

if __name__ == "__main__":
    asyncio.run(main())
