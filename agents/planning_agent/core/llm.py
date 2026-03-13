import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load from root .env file
root_dir = Path(__file__).parent.parent.parent.parent
load_dotenv(root_dir / ".env")


class ClaudeLLM:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env")

        self.model = os.getenv(
            "CLAUDE_MODEL",
            "claude-3-5-sonnet-20240620"  # safe default
        )

        self.client = Anthropic(api_key=api_key)

    def generate(self, prompt: str, max_tokens: int = 1500) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

        except Exception as e:
            raise RuntimeError(
                f"Claude model error (model={self.model}): {str(e)}"
            )
