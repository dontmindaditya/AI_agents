"""
LLM Service - Manage multiple LLM providers
"""
from typing import Optional, Dict, Any, List
from langchain_core.language_models import BaseChatModel

from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Import LangChain providers with optional fallbacks
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("langchain-openai not installed. OpenAI models will not be available.")

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("langchain-anthropic not installed. Anthropic models will not be available.")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.warning("langchain-google-genai not installed. Google models will not be available.")


class LLMService:
    """Service for managing LLM providers"""
    
    def __init__(self):
        self._models: Dict[str, BaseChatModel] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available LLM models"""
        try:
            # OpenAI
            if settings.OPENAI_API_KEY and OPENAI_AVAILABLE:
                self._models['openai'] = ChatOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    model=settings.DEFAULT_MODEL,
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                logger.info("OpenAI model initialized")
            elif settings.OPENAI_API_KEY and not OPENAI_AVAILABLE:
                logger.warning("OpenAI API key found but langchain-openai not installed. Run: pip install langchain-openai")
            
            # Anthropic
            if settings.ANTHROPIC_API_KEY and ANTHROPIC_AVAILABLE:
                self._models['anthropic'] = ChatAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model="claude-3-sonnet-20240229",
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                logger.info("Anthropic model initialized")
            elif settings.ANTHROPIC_API_KEY and not ANTHROPIC_AVAILABLE:
                logger.warning("Anthropic API key found but langchain-anthropic not installed. Run: pip install langchain-anthropic")
            
            # Google / Gemini
            google_key = settings.GOOGLE_API_KEY or settings.GEMINI_API_KEY
            if google_key and GOOGLE_AVAILABLE:
                self._models['google'] = ChatGoogleGenerativeAI(
                    google_api_key=google_key,
                    model="gemini-pro",
                    temperature=settings.TEMPERATURE,
                    max_output_tokens=settings.MAX_TOKENS
                )
                logger.info("Google/Gemini model initialized")
            elif google_key and not GOOGLE_AVAILABLE:
                logger.warning("Google API key found but langchain-google-genai not installed. Run: pip install langchain-google-genai")
            
            # Groq (uses OpenAI-compatible interface)
            if settings.GROQ_API_KEY and OPENAI_AVAILABLE:
                self._models['groq'] = ChatOpenAI(
                    api_key=settings.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1",
                    model="mixtral-8x7b-32768",
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                logger.info("Groq model initialized")
            elif settings.GROQ_API_KEY and not OPENAI_AVAILABLE:
                logger.warning("Groq API key found but langchain-openai not installed (needed for Groq). Run: pip install langchain-openai")
            
            if not self._models:
                logger.warning("No LLM providers initialized. Please configure API keys and install required packages.")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
    
    def get_model(self, provider: Optional[str] = None) -> BaseChatModel:
        """
        Get LLM model by provider
        
        Args:
            provider: Provider name (openai, anthropic, google, groq)
            
        Returns:
            LLM model instance
        """
        provider = provider or settings.DEFAULT_LLM_PROVIDER
        
        if provider not in self._models:
            logger.warning(f"Provider '{provider}' not available, falling back to default")
            provider = settings.DEFAULT_LLM_PROVIDER
        
        if provider not in self._models:
            raise ValueError(f"No LLM providers available. Please configure API keys.")
        
        return self._models[provider]
    
    def list_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self._models.keys())
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if provider is available"""
        return provider in self._models
    
    async def generate_response(
        self,
        prompt: str,
        provider: Optional[str] = None,
        system_message: Optional[str] = None
    ) -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: User prompt
            provider: LLM provider
            system_message: Optional system message
            
        Returns:
            Generated response
        """
        try:
            model = self.get_model(provider)
            
            messages = []
            if system_message:
                messages.append(("system", system_message))
            messages.append(("human", prompt))
            
            response = await model.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise
    
    def generate_response_sync(
        self,
        prompt: str,
        provider: Optional[str] = None,
        system_message: Optional[str] = None
    ) -> str:
        """
        Generate response from LLM (synchronous)
        
        Args:
            prompt: User prompt
            provider: LLM provider
            system_message: Optional system message
            
        Returns:
            Generated response
        """
        try:
            model = self.get_model(provider)
            
            messages = []
            if system_message:
                messages.append(("system", system_message))
            messages.append(("human", prompt))
            
            response = model.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise


# Global instance
llm_service = LLMService()