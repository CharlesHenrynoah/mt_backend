from ..core.base_agent import BaseAgent
from ..core.message_types import MessageType
import jwt
import datetime
from typing import Dict

class AuthAgent(BaseAgent):
    """Agent responsable de l'authentification et de la gestion des sessions"""
    
    class AuthenticationBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if msg.get_metadata("type") == MessageType.AUTH_REQUEST.value:
                    try:
                        # Traiter la demande d'authentification
                        credentials = eval(msg.body)
                        token = self.agent.authenticate(credentials)
                        
                        # Envoyer la réponse
                        response = Message(to=str(msg.sender))
                        response.body = token
                        response.set_metadata("type", MessageType.AUTH_RESPONSE.value)
                        await self.send(response)
                        
                    except Exception as e:
                        # Envoyer une réponse d'erreur
                        error_msg = Message(to=str(msg.sender))
                        error_msg.body = str(e)
                        error_msg.set_metadata("type", MessageType.ERROR.value)
                        await self.send(error_msg)
    
    def __init__(self, jid, password, secret_key="votre_clé_secrète"):
        super().__init__(jid, password)
        self.secret_key = secret_key
        self.users = {}  # En production, utiliser une base de données
        
    async def setup(self):
        await super().setup()
        self.add_cyclic_behaviour(self.AuthenticationBehaviour)
        
    def authenticate(self, credentials: Dict) -> str:
        """Authentifie un utilisateur et génère un token JWT"""
        username = credentials.get("username")
        password = credentials.get("password")
        
        # En production, vérifier les credentials dans une base de données
        if username in self.users and self.users[username] == password:
            token = jwt.encode({
                "sub": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, self.secret_key, algorithm="HS256")
            return token
        else:
            raise ValueError("Invalid credentials")
