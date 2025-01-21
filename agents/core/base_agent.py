from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import logging

class BaseAgent(Agent):
    """Agent de base avec des fonctionnalités communes"""
    
    def __init__(self, jid, password, log_level=logging.INFO):
        super().__init__(jid, password)
        self.logger = logging.getLogger(str(jid))
        self.logger.setLevel(log_level)
        
    async def setup(self):
        """Configuration initiale de l'agent"""
        self.logger.info(f"Agent {str(self.jid)} démarré")
        
    async def send_message(self, to_jid, content, metadata=None):
        """Envoie un message à un autre agent"""
        msg = Message(to=str(to_jid))
        msg.body = content
        if metadata:
            for key, value in metadata.items():
                msg.set_metadata(key, value)
        await self.send(msg)
        self.logger.debug(f"Message envoyé à {to_jid}: {content}")
        
    def add_cyclic_behaviour(self, behaviour_class, **kwargs):
        """Ajoute un comportement cyclique à l'agent"""
        behaviour = behaviour_class(**kwargs)
        self.add_behaviour(behaviour)
        return behaviour
