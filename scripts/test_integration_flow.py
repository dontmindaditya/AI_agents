
import asyncio
import sys
import os
import json
import httpx
from dotenv import load_dotenv

# Load env variables
root_dir = os.path.join(os.path.dirname(__file__), "..", "..")
if os.path.exists(os.path.join(root_dir, ".env")):
    load_dotenv(os.path.join(root_dir, ".env"))

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from database.client import supabase_client
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

PROJECT_ID = "demo-project"
API_URL = "http://127.0.0.1:8000"

async def test_integration():
    print(f"Testing integration for project: {PROJECT_ID}")
    
    # 1. Get Agent ID
    print("1. Fetching Help Bot ID...")
    res = supabase_client.client.table("agent_catalog").select("id").eq("slug", "help-bot").single().execute()
    if not res.data:
        print("Help Bot not found")
        return
    agent_id = res.data['id']
    print(f"   Agent ID: {agent_id}")

    # 2. Clean up existing install
    print("2. Cleaning up previous installs...")
    supabase_client.client.table("project_agents").delete().eq("project_id", PROJECT_ID).execute()
    
    # 3. Install Agent via API
    print("3. Installing agent via API...")
    async with httpx.AsyncClient() as client:
        # We need to install directly or simulate the API call? 
        # Using httpx to call the running backend (requires backend to be running!)
        # If backend is not running, we can't test API.
        # Assuming user has backend running as per notifications.
        
        try:
            resp = await client.post(
                f"{API_URL}/api/projects/{PROJECT_ID}/agents",
                json={"agent_id": agent_id, "config": {"welcome_message": "Test Hello"}}
            )
            if resp.status_code != 200:
                print(f"Install failed: {resp.text}")
                return
            print("   Installed successfully via API")
        except Exception as e:
             print(f"Connection failed (is backend running?): {e}")
             return

    # 4. Trigger Refresh via API
    print("4. Triggering Refresh (Hot Reload)...")
    async with httpx.AsyncClient() as client:
        try:
            # We need to mock "orchestrator state" availability.
            # If the backend was just started, it has no active pipelines.
            # The refresh endpoint throws 404 if project not active.
            # This makes testing hard without a running session.
            
            resp = await client.post(f"{API_URL}/api/projects/{PROJECT_ID}/refresh-agents")
            
            if resp.status_code == 200:
                print("   Refresh triggered successfully")
                print(f"   Response: {resp.json()}")
            elif resp.status_code == 404:
                print("   Refresh skipped: Project session not active (Expected if no frontend connected)")
            else:
                 print(f"Refresh failed: {resp.text}")

        except Exception as e:
             print(f"Connection failed: {e}")

    # 5. Verify Database State
    print("5. Verifying DB state...")
    res = supabase_client.client.table("project_agents").select("*").eq("project_id", PROJECT_ID).execute()
    if len(res.data) > 0:
        print(f"   DB shows agent installed: {res.data[0]['config']}")
    else:
        print("   DB check failed")

if __name__ == "__main__":
    asyncio.run(test_integration())
