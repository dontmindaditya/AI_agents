import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Literal

# Load from root .env file
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# LLM Configuration
LLM_PROVIDER: Literal["openai", "anthropic", "google"] = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("GPT_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Agent Configuration
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"

# Frontend Frameworks
SUPPORTED_FRAMEWORKS = ["react", "vue", "vanilla"]
DEFAULT_FRAMEWORK = "react"

# Output Configuration
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")