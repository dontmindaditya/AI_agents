
import asyncio
import sys
import os
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

async def verify():
    print("Verifying agents...")
    try:
        res = supabase_client.client.table("agent_catalog").select("name, slug, is_active").execute()
        if not res.data:
            print("No agents found in catalog!")
        else:
            print(f"Found {len(res.data)} agents:")
            for agent in res.data:
                status = "Active" if agent['is_active'] else "Inactive"
                print(f"   - {agent['name']} ({agent['slug']}) [{status}]")
    except Exception as e:
        print(f"Error verifying agents: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
