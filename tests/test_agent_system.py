import sys
from pathlib import Path
import asyncio

# Add backend to sys path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from agents.registry import agent_registry

async def test_agent_system():
    print("🧪 Testing Agent System...")
    
    # 1. Test Discovery
    print("\n1. Testing Registry Discovery...")
    agents = agent_registry.get_all_agents()
    print(f"Found {len(agents)} agents.")
    for a in agents:
        print(f" - [{a['id']}] {a['name']}")
    
    # Check if text_processor is found
    tp = next((a for a in agents if a['id'] == 'text_processor'), None)
    if not tp:
        print("❌ 'text_processor' agent not found!")
        return
    print("✅ 'text_processor' found.")

    # 2. Test Execution
    print("\n2. Testing Agent Execution (text_processor)...")
    agent_class = agent_registry.get_agent_class('text_processor')
    agent = agent_class()
    
    inputs = {"text": "hello world", "operation": "uppercase"}
    print(f"Input: {inputs}")
    
    result = await agent.run(inputs)
    print(f"Result: {result}")
    
    if result.get("result") == "HELLO WORLD":
        print("✅ Execution successful!")
    else:
        print("❌ Execution failed or unexpected result.")

if __name__ == "__main__":
    asyncio.run(test_agent_system())
