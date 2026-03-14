"""OpenAI GPT API Client

This module provides a client for interacting with OpenAI's GPT API.
"""

from typing import Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings, AI_MODELS
from utils.logger import setup_logger

logger = setup_logger(__name__)


class OpenAIClient:
    """Client for OpenAI GPT API"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.config = AI_MODELS["gpt4"]
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
            logger.error(f"GPT-4 generation failed: {e}")
            raise
    
    async def stream_generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        """Stream generation"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"GPT-4 streaming failed: {e}")
            raise