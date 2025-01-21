from ..core.base_agent import BaseAgent
from ..core.message_types import MessageType
import aiohttp
import json
from typing import Dict, Any

class ExternalAgent(BaseAgent):
    """Agent responsable de la communication avec les services externes"""
    
    class ExternalCommunicationBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.get_metadata("type") == MessageType.EXTERNAL_REQUEST.value:
                try:
                    # Traiter la requête externe
                    request_data = json.loads(msg.body)
                    response_data = await self.agent.handle_external_request(request_data)
                    
                    # Envoyer la réponse
                    response = Message(to=str(msg.sender))
                    response.body = json.dumps(response_data)
                    response.set_metadata("type", MessageType.EXTERNAL_RESPONSE.value)
                    await self.send(response)
                    
                except Exception as e:
                    error_msg = Message(to=str(msg.sender))
                    error_msg.body = str(e)
                    error_msg.set_metadata("type", MessageType.ERROR.value)
                    await self.send(error_msg)
    
    def __init__(self, jid, password, api_keys: Dict[str, str] = None):
        super().__init__(jid, password)
        self.api_keys = api_keys or {}
        self.session = None
    
    async def setup(self):
        await super().setup()
        self.session = aiohttp.ClientSession()
        self.add_cyclic_behaviour(self.ExternalCommunicationBehaviour)
    
    async def handle_external_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gère les requêtes vers des services externes"""
        service = request_data.get("service")
        method = request_data.get("method", "GET")
        endpoint = request_data.get("endpoint")
        data = request_data.get("data")
        
        if not service or not endpoint:
            raise ValueError("Service et endpoint sont requis")
        
        return await self.make_external_request(service, method, endpoint, data)
    
    async def make_external_request(self, service: str, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Effectue une requête vers un service externe"""
        # Construire l'URL et les headers
        base_url = self.get_service_url(service)
        url = f"{base_url}{endpoint}"
        headers = self.get_service_headers(service)
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Erreur {response.status}: {error_text}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la requête vers {service}: {str(e)}")
            raise
    
    def get_service_url(self, service: str) -> str:
        """Retourne l'URL de base pour un service"""
        # Définir les URLs de base pour chaque service
        service_urls = {
            "fiverr": "https://api.fiverr.com/v1",
            "github": "https://api.github.com",
            # Ajouter d'autres services au besoin
        }
        
        if service not in service_urls:
            raise ValueError(f"Service non supporté: {service}")
        
        return service_urls[service]
    
    def get_service_headers(self, service: str) -> Dict[str, str]:
        """Retourne les headers nécessaires pour un service"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "MT-Backend/1.0"
        }
        
        # Ajouter l'API key si disponible
        if service in self.api_keys:
            headers["Authorization"] = f"Bearer {self.api_keys[service]}"
        
        return headers
    
    async def cleanup(self):
        """Nettoie les ressources lors de l'arrêt de l'agent"""
        if self.session:
            await self.session.close()
