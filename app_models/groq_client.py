"""Groq API Client

This module provides a client for interacting with Groq's API.
"""

from typing import Optional
from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings, AI_MODELS
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GroqClient:
    """Client for Groq API"""
    
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.config = AI_MODELS["groq"]
        self.model = self.config["model"]
    
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
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.config["max_tokens"],
                temperature=temperature or self.config["temperature"],
                **kwargs
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise