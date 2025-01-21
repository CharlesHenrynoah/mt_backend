from ..core.base_agent import BaseAgent
from ..core.message_types import MessageType
import pandas as pd
import json

class DataAgent(BaseAgent):
    """Agent responsable du traitement et de l'analyse des données"""
    
    class DataProcessingBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.get_metadata("type") == MessageType.DATA_REQUEST.value:
                try:
                    # Traiter la demande de données
                    data_request = json.loads(msg.body)
                    processed_data = await self.agent.process_data(data_request)
                    
                    # Envoyer la réponse
                    response = Message(to=str(msg.sender))
                    response.body = json.dumps(processed_data)
                    response.set_metadata("type", MessageType.DATA_RESPONSE.value)
                    await self.send(response)
                    
                except Exception as e:
                    error_msg = Message(to=str(msg.sender))
                    error_msg.body = str(e)
                    error_msg.set_metadata("type", MessageType.ERROR.value)
                    await self.send(error_msg)
    
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.data_cache = {}
    
    async def setup(self):
        await super().setup()
        self.add_cyclic_behaviour(self.DataProcessingBehaviour)
        
    async def process_data(self, data_request):
        """Traite les données selon la requête"""
        request_type = data_request.get("type")
        data = data_request.get("data")
        
        if request_type == "filter":
            return self.filter_data(data, data_request.get("criteria", {}))
        elif request_type == "analyze":
            return self.analyze_data(data)
        else:
            raise ValueError(f"Type de requête non supporté: {request_type}")
    
    def filter_data(self, data, criteria):
        """Filtre les données selon les critères"""
        df = pd.DataFrame(data)
        
        for column, value in criteria.items():
            if column in df.columns:
                df = df[df[column] == value]
        
        return df.to_dict('records')
    
    def analyze_data(self, data):
        """Analyse les données et retourne des statistiques"""
        df = pd.DataFrame(data)
        
        analysis = {
            "count": len(df),
            "summary": df.describe().to_dict(),
            "columns": list(df.columns)
        }
        
        return analysis
