import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration des agents
AGENT_PASSWORD = "your_password_here"  # À changer en production

# JIDs des agents
USER_AGENT_JID = "user_agent@localhost"
AUTH_AGENT_JID = "auth_agent@localhost"
SEARCH_AGENT_JID = "search_agent@localhost"
DATA_AGENT_JID = "data_agent@localhost"
EXTERNAL_AGENT_JID = "external_agent@localhost"

# Clés API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD8LKVDXO5zAFYbINcKHII-fiDa6rDexR4")
FIVERR_API_KEY = os.getenv("FIVERR_API_KEY", "")

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mt_backend.db")

# Configuration Redis pour le cache
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Configuration du logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Autres configurations
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key_here")  # À changer en production
TOKEN_EXPIRATION = 3600  # 1 heure
