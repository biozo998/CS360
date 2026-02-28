import os
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

class Config:
    """Base configuration."""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cs360")
    
    # PSOffice API
    PSOFFICE_API_URL = os.getenv("PSOFFICE_API_URL", "https://api.psofficeapp.com.br/csintegra")
    PSOFFICE_API_TOKEN = os.getenv("PSOFFICE_API_TOKEN", "")
    
    # Agile API
    AGILE_API_URL = os.getenv("AGILE_API_URL", "https://api.agile.psofficeapp.com.br/csintegra")
    AGILE_OAUTH_URL = os.getenv("AGILE_OAUTH_URL", "https://pso-csintegra.jexperts.cloud/api/oauth/token")
    AGILE_CLIENT_ID = os.getenv("AGILE_CLIENT_ID", "")
    AGILE_CLIENT_SECRET = os.getenv("AGILE_CLIENT_SECRET", "")
    
    # App Setting
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-dev-key")

config = Config()
