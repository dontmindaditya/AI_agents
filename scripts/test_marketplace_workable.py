"""
Quick test script to verify the marketplace is workable
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load env
root_dir = os.path.join(os.path.dirname(__file__), "..", "..")
if os.path.exists(os.path.join(root_dir, ".env")):
    load_dotenv(os.path.join(root_dir, ".env"))

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.client import supabase_client

async def test_marketplace():
    print("=" * 60)
    print("MARKETPLACE WORKABILITY TEST")
    print("=" * 60)
    
    # Test 1: Database Connection
    print("\n[1/4] Testing database connection...")
    try:
        res = supabase_client.client.table("agent_catalog").select("count").execute()
        print(f"   [OK] Database connected")
    except Exception as e:
        print(f"   [FAIL] Database error: {e}")
        return False
    
    # Test 2: Agent Catalog
    print("\n[2/4] Checking agent catalog...")
    try:
        res = supabase_client.client.table("agent_catalog").select("name, slug").execute()
        if res.data:
            print(f"   [OK] Found {len(res.data)} agents:")
            for agent in res.data:
                print(f"      - {agent['name']} ({agent['slug']})")
        else:
            print("   [FAIL] No agents found. Run: python backend/scripts/seed_agents.py")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False
    
    # Test 3: Agent Imports
    print("\n[3/4] Testing agent imports...")
    try:
        from agents.planner_agent import PlannerAgent
        from agents.frontend_agent import FrontendAgent
        from agents.backend_agent import BackendAgent
        print("   [OK] All core agents imported successfully")
    except Exception as e:
        print(f"   [FAIL] Import error: {e}")
        return False
    
    # Test 4: Integration Stage
    print("\n[4/4] Testing integration stage...")
    try:
        from pipeline.integration_stage import IntegrationStage
        print("   [OK] Integration stage available")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - MARKETPLACE IS WORKABLE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start backend: python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload")
    print("2. Visit: http://localhost:3000/builder")
    print("3. Click 'Agents' button and select an agent")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_marketplace())
    sys.exit(0 if result else 1)
