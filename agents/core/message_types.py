from enum import Enum

class MessageType(Enum):
    """Types de messages échangés entre les agents"""
    
    # Messages d'authentification
    AUTH_REQUEST = "auth_request"
    AUTH_RESPONSE = "auth_response"
    
    # Messages de recherche
    SEARCH_REQUEST = "search_request"
    SEARCH_RESPONSE = "search_response"
    
    # Messages de traitement des données
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    
    # Messages de communication externe
    EXTERNAL_REQUEST = "external_request"
    EXTERNAL_RESPONSE = "external_response"
    
    # Messages de statut
    STATUS_UPDATE = "status_update"
    ERROR = "error"
