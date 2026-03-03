"""Anthropic Claude API Client"""

from typing import Optional
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings, AI_MODELS
from utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeClient:
    """Client for Anthropic Claude API"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.config = AI_MODELS["claude"]
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
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.config["max_tokens"],
                temperature=temperature or self.config["temperature"],
                system=system_prompt or "",
                messages=messages,
                **kwargs
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise
    
    async def stream_generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        """Stream generation"""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                system=system_prompt or "",
                messages=messages,
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Claude streaming failed: {e}")
            raise