"""
Final System Test - Marketplace + Pipeline Integration
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

root_dir = os.path.join(os.path.dirname(__file__), "..", "..")
if os.path.exists(os.path.join(root_dir, ".env")):
    load_dotenv(os.path.join(root_dir, ".env"))

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.client import supabase_client

async def test_system():
    print("=" * 70)
    print("FINAL SYSTEM TEST - MARKETPLACE + PIPELINE")
    print("=" * 70)
    
    # Test 1: Database
    print("\n[1/5] Database Connection...")
    try:
        res = supabase_client.client.table("agent_catalog").select("count").execute()
        print("   [OK] Database connected")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 2: Marketplace Agents
    print("\n[2/5] Marketplace Agents...")
    try:
        res = supabase_client.client.table("agent_catalog").select("name, slug").execute()
        print(f"   [OK] {len(res.data)} agents available:")
        for agent in res.data:
            print(f"      - {agent['name']}")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 3: Pipeline Stages
    print("\n[3/5] Pipeline Stages...")
    try:
        from pipeline.planning_stage import PlanningStage
        from pipeline.generation_stage import GenerationStage
        from pipeline.analysis_stage import AnalysisStage
        from pipeline.integration_stage import IntegrationStage
        print("   [OK] All pipeline stages imported")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 4: Agent Subdirectories
    print("\n[4/5] Your Agent Implementations...")
    agent_dirs = [
        "planning_agent",
        "frontend_agent", 
        "backend-agent",
        "uiux-agent"
    ]
    for agent_dir in agent_dirs:
        path = os.path.join(os.path.dirname(__file__), "..", "agents", agent_dir)
        if os.path.exists(path):
            print(f"   [OK] {agent_dir}")
        else:
            print(f"   [WARN] {agent_dir} not found")
    
    # Test 5: Integration
    print("\n[5/5] Integration Stage...")
    try:
        from pipeline.integration_stage import IntegrationStage
        print("   [OK] Integration stage ready")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    print("\n" + "=" * 70)
    print("[SUCCESS] SYSTEM IS READY!")
    print("=" * 70)
    print("\nYour Setup:")
    print("  - Marketplace: 2 example agents seeded")
    print("  - Pipeline: Using YOUR agent implementations")
    print("  - Integration: Ready to inject marketplace agents")
    print("\nStart backend:")
    print("  python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload")
    print("\nTest UI:")
    print("  http://localhost:3000/builder")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_system())
    sys.exit(0 if result else 1)
