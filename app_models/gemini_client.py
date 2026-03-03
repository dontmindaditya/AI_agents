"""Google Gemini API Client"""

from typing import Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings, AI_MODELS
from utils.logger import get_logger

logger = get_logger(__name__)


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.config = AI_MODELS["gemini"]
        self.model = genai.GenerativeModel(self.config["model"])
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """Generate completion"""
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            generation_config = {
                "temperature": temperature or self.config["temperature"],
                "max_output_tokens": max_tokens or self.config["max_tokens"],
            }
            
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise