import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATAFORSEO_LOGIN = os.getenv('DATAFORSEO_LOGIN')
    DATAFORSEO_PASSWORD = os.getenv('DATAFORSEO_PASSWORD')
    GOOGLE_CLOUD_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # DataForSEO API endpoints
    DATAFORSEO_BASE_URL = "https://api.dataforseo.com/v3"
    
    # Google Ranking API settings
    GOOGLE_RANKING_MODEL = "semantic-ranker-default@latest"
    GOOGLE_RANKING_LOCATION = "global"
    GOOGLE_RANKING_CONFIG = "default_ranking_config"
    
    # Crawler settings
    MAX_CONTENT_LENGTH = 5000  # Max characters to extract from each page
    REQUEST_TIMEOUT = 30
    MAX_CONCURRENT_REQUESTS = 5 