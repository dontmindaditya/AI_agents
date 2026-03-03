"""
LLM Client wrapper supporting OpenAI and Anthropic
"""
from typing import Optional, List, Dict, Any
import openai
from anthropic import Anthropic
from config import settings


class LLMClient:
    """Unified LLM client for OpenAI and Anthropic"""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.default_llm_provider
        self._initialized = False
        self.anthropic_client = None
        self.model = None
    
    def _initialize(self):
        """Lazy initialization of the LLM client"""
        if self._initialized:
            return
        
        if self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError(
                    "OpenAI API key not configured. "
                    "Please set OPENAI_API_KEY in your .env file"
                )
            openai.api_key = settings.openai_api_key
            self.model = settings.openai_model
        elif self.provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError(
                    "Anthropic API key not configured. "
                    "Please set ANTHROPIC_API_KEY in your .env file"
                )
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        self._initialized = True
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        images: Optional[List[str]] = None
    ) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            images: List of image URLs or base64 strings
        
        Returns:
            Generated text response
        """
        self._initialize()  # Initialize on first use
        
        if self.provider == "openai":
            return self._generate_openai(prompt, system_prompt, temperature, max_tokens, images)
        else:
            return self._generate_anthropic(prompt, system_prompt, temperature, max_tokens, images)
    
    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        images: Optional[List[str]]
    ) -> str:
        """Generate using OpenAI API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Handle images for vision models
        if images:
            content = [{"type": "text", "text": prompt}]
            for img in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img}
                })
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": prompt})
        
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        images: Optional[List[str]]
    ) -> str:
        """Generate using Anthropic API"""
        # Prepare message content
        if images:
            content = []
            for img in images:
                # Assuming base64 encoded images
                if img.startswith("data:image"):
                    # Extract base64 data
                    img_data = img.split(",")[1]
                    media_type = img.split(";")[0].split(":")[1]
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_data
                        }
                    })
            content.append({"type": "text", "text": prompt})
        else:
            content = prompt
        
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": content}]
        )
        
        return response.content[0].text
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            schema: JSON schema for structured output
        
        Returns:
            Parsed JSON response
        """
        self._initialize()  # Initialize on first use
        
        import json
        
        json_instruction = "\n\nRespond ONLY with valid JSON. No explanation or markdown."
        if schema:
            json_instruction += f"\n\nFollow this schema: {json.dumps(schema)}"
        
        full_prompt = prompt + json_instruction
        response = self.generate(full_prompt, system_prompt, temperature=0.3)
        
        # Clean response (remove markdown code blocks if present)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        return json.loads(response.strip())


# Global LLM client instance (lazily initialized)
llm_client = LLMClient()