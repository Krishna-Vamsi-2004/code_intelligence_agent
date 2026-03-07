
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Import services
from services.working_llm_service import WorkingLLMService
from services.retry_engine import RetryEngine
from services.validation_service import ValidationService
from services.kroki_service import KrokiService
from services.mermaid_cli_service import MermaidCLIService
from services.score_service import ScoreService

class ServiceContainer:
    _instance = None
    
    def __init__(self):
        # Get configuration from environment
        max_retries = int(os.getenv('MAX_RETRIES', '2'))
        
        # Initialize Working LLM Service (supports Ollama, OpenRouter, and templates)
        try:
            print(f"🤖 Using Working LLM Service (Ollama/Templates)")
            self.llm = WorkingLLMService()
        except Exception as e:
            print(f"⚠️  LLM initialization failed: {e}")
            raise
        
        self.retry_engine = RetryEngine(self.llm, max_retries=max_retries)
        self.validator = ValidationService()
        self.kroki = KrokiService()
        self.mermaid_cli = MermaidCLIService()
        self.score = ScoreService()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ServiceContainer()
        return cls._instance

def get_services():
    return ServiceContainer.get_instance()
