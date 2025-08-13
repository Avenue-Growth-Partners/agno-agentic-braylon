"""
Configuration module for AGP Intelligence system.
Centralizes all environment variables and constants.
"""
import os

class Config:
    """Configuration class containing all environment variables and constants."""
    
    # API Keys
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "<DEFAULT_VAL>")
    SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "<DEFAULT_VAL>")
    GRATA_API_KEY = os.environ.get("GRATA_API_KEY", "<DEFAULT_VAL>")
    HUBSPOT_ACCESS_TOKEN = os.environ.get('HUBSPOT_API_KEY', "<DEFAULT_VAL>")
    JINA_KEY = os.environ.get("JINA_KEY", "<DEFAULT_VAL>")
    
    # Grata API Configuration
    GRATA_API_VERSION = "v1.4"
    GRATA_BULK_ENRICH_BATCH_SIZE = 100
    
    # Processing Configuration
    DEFAULT_BATCH_SIZE = 15
    DEFAULT_NUM_WORKERS = 4
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 2
    RATE_LIMIT_PER_MINUTE = 30
    
    # HubSpot Owner ID to Name Mapping
    HUBSPOT_OWNER_MAP = {
        "76607939": "Wells Johnstone",
        "78406070": "Annie Rosen",
        "78670087": "Ryan Russell",
        "79267418": "Brian Goldsmith",
        "79269423": "Harish Ramani",
        "87420032": "Diana Stettner",
        "104211884": "Oscar Lee",
        "181980857": "Scott Brinkman",
        "725097754": "Alejandra Osorio",
        "774806655": "Emily Young"
    }
    
    # Fine-tuned Model IDs
    AI_NATIVE_MODEL_ID = "ft:gpt-4o-mini-2024-07-18:avenuegp::AVGq90Nb"
    VERTICAL_MODEL_ID = "ft:gpt-4o-mini-2024-07-18:avenuegp::AWILSieS"
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        required_keys = [
            cls.OPENAI_API_KEY,
            cls.GRATA_API_KEY,
            cls.HUBSPOT_ACCESS_TOKEN,
            cls.JINA_KEY
        ]
        
        missing_keys = [key for key in required_keys if key == "<DEFAULT_VAL>"]
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {missing_keys}")