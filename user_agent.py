import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import google.generativeai as genai
from config import GEMINI_API_KEY, USER_AGENT_JID, URL_AGENT_JID, AGENT_PASSWORD

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

class UserInterfaceAgent(Agent):
    class HandleUserInput(CyclicBehaviour):
        async def run(self):
            try:
                # Demander l'entrée utilisateur
                query = input("\nQue recherchez-vous ? (ou 'quit' pour quitter) : ")
                
                if query.lower() == 'quit':
                    await self.agent.stop()
                    return
                
                print("\nTraitement de votre requête...\n")
                
                # Envoyer la requête à l'agent URL
                msg = Message(to=URL_AGENT_JID)
                msg.body = query
                msg.set_metadata("performative", "request")
                await self.send(msg)
                
                # Attendre la réponse
                response = await self.receive(timeout=60)
                if response:
                    print("\nRésultats de la recherche :")
                    print("-" * 50)
                    print(response.body)
                    print("-" * 50)
                else:
                    print("\nPas de réponse reçue dans le délai imparti.")
                
            except Exception as e:
                print(f"\nErreur lors du traitement de votre requête : {str(e)}")
                print("Veuillez réessayer.")

    class HandleResponses(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print("\nNouveau message reçu :")
                print("-" * 50)
                print(msg.body)
                print("-" * 50)

    async def setup(self):
        print("Agent Interface Utilisateur démarré")
        behaviour1 = self.HandleUserInput()
        behaviour2 = self.HandleResponses()
        self.add_behaviour(behaviour1)
        self.add_behaviour(behaviour2)

if __name__ == "__main__":
    user_agent = UserInterfaceAgent(USER_AGENT_JID, AGENT_PASSWORD)
    user_agent.start()
