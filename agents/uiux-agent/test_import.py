"""
Quick test script to verify the agent is working
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env files from root
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env", override=True)

print("🔍 Checking environment variables...")
print()

# Check OpenAI
openai_key = os.getenv("OPENAI_API_KEY", "")
if openai_key:
    print(f"✅ OPENAI_API_KEY: {openai_key[:8]}...{openai_key[-4:]} (length: {len(openai_key)})")
else:
    print("❌ OPENAI_API_KEY: Not set")

# Check Anthropic
anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
if anthropic_key:
    print(f"✅ ANTHROPIC_API_KEY: {anthropic_key[:8]}...{anthropic_key[-4:]} (length: {len(anthropic_key)})")
else:
    print("❌ ANTHROPIC_API_KEY: Not set")

# Check provider
provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
print(f"✅ DEFAULT_LLM_PROVIDER: {provider}")
print()

# Try importing
print("🔍 Testing imports...")
try:
    from config import settings
    print(f"✅ Config loaded successfully")
    print(f"   Provider: {settings.default_llm_provider}")
    print(f"   Has OpenAI key: {bool(settings.openai_api_key)}")
    print(f"   Has Anthropic key: {bool(settings.anthropic_api_key)}")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    exit(1)

print()
print("🔍 Testing LLM client...")
try:
    from utils.llm_client import llm_client
    print(f"✅ LLM client imported successfully")
    print(f"   Provider: {llm_client.provider}")
    print(f"   Note: Client will initialize on first use")
except Exception as e:
    print(f"❌ LLM client import failed: {e}")
    exit(1)

print()
print("🔍 Testing agents...")
try:
    from agents import OrchestratorAgent
    print(f"✅ Orchestrator imported successfully")
except Exception as e:
    print(f"❌ Orchestrator import failed: {e}")
    exit(1)

print()
print("=" * 50)
print("✅ ALL TESTS PASSED!")
print("=" * 50)
print()
print("You can now run:")
print("  python main.py analyze your-image.png")