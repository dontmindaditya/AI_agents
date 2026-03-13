"""Integration Stage"""

import json
import re
from typing import Dict, Any, List
from database.client import supabase_client
from utils.logger import get_logger
from services.websocket_manager import WebSocketManager

logger = get_logger(__name__)

class IntegrationStage:
    """Agent Integration Stage"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.ws_manager = websocket_manager
    
    async def execute(self, project_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration"""
        try:
            # 1. Fetch selected agents for the project
            project_agents = self._fetch_project_agents(project_id)
            
            if not project_agents:
                logger.info(f"No agents to integrate for project {project_id}")
                return {"integrated_agents": 0}

            logger.info(f" integrating {len(project_agents)} agents for project {project_id}")
            
            # 2. Get existing files from context
            all_files = context.get("all_files", [])
            files_map = {f["path"]: f for f in all_files}
            
            # 3. Process each agent
            for pa in project_agents:
                agent = pa["agent"]
                config = pa["config"]
                
                # A. Inject Frontend Component
                if agent.get("frontend_component_code"):
                    component_path = f"src/components/agents/{agent['slug']}.tsx"
                    files_map[component_path] = {
                        "path": component_path,
                        "content": agent["frontend_component_code"],
                        "type": "component"
                    }
                    
                # B. Inject Backend API
                if agent.get("backend_api_code"):
                    api_path = f"src/app/api/agents/{agent['slug']}/route.ts"
                    files_map[api_path] = {
                        "path": api_path,
                        "content": agent["backend_api_code"],
                        "type": "api"
                    }
                    
                # C. Update Dependencies
                if agent.get("dependencies"):
                    self._update_package_json(files_map, agent["dependencies"])
                    
                # D. Inject into Layout
                self._inject_into_layout(files_map, agent["slug"], agent["name"])

            # 4. Update context
            updated_files = list(files_map.values())
            context["all_files"] = updated_files
            
            return {
                "integrated_agents": len(project_agents),
                "total_files": len(updated_files)
            }
            
        except Exception as e:
            logger.error(f"Integration failed: {e}")
            raise

    def _fetch_project_agents(self, project_id: str) -> List[Dict[str, Any]]:
        """Fetch agents installed in the project"""
        res = supabase_client.client.table("project_agents")\
            .select("*, agent:agent_catalog(*)")\
            .eq("project_id", project_id)\
            .eq("is_enabled", True)\
            .execute()
        return res.data

    def _update_package_json(self, files_map: Dict[str, Any], new_deps: Dict[str, str]):
        """Update package.json with new dependencies"""
        pkg_file = files_map.get("package.json")
        if not pkg_file:
            return # Should not happen if generation ran first
            
        try:
            content = json.loads(pkg_file["content"])
            deps = content.get("dependencies", {})
            
            for name, version in new_deps.items():
                deps[name] = version
                
            content["dependencies"] = deps
            pkg_file["content"] = json.dumps(content, indent=2)
        except Exception as e:
            logger.warning(f"Failed to update package.json: {e}")

    def _inject_into_layout(self, files_map: Dict[str, Any], agent_slug: str, agent_name: str):
        """Inject agent component into layout.tsx"""
        layout_file = files_map.get("src/app/layout.tsx")
        # Fallback to root layout if src/app doesn't exist? (Project structure seems to be src/app)
        if not layout_file:
            # Try finding any layout
            for path in files_map:
                if path.endswith("layout.tsx"):
                    layout_file = files_map[path]
                    break
        
        if not layout_file:
            logger.warning("Layout file not found, skipping injection")
            return

        content = layout_file["content"]
        
        # 1. Add Import
        component_name = self._to_pascal_case(agent_slug)
        import_stmt = f"import {component_name} from '@/components/agents/{agent_slug}';"
        
        if import_stmt not in content:
            # Insert after last import
            last_import_idx = content.rfind("import ")
            if last_import_idx != -1:
                end_of_line = content.find("\n", last_import_idx) + 1
                content = content[:end_of_line] + import_stmt + "\n" + content[end_of_line:]
            else:
                content = import_stmt + "\n" + content

        # 2. Add Component usage before </body>
        # We look for {children} usually, but inserting before </body> is safer for overlays
        usage_stmt = f"        <{component_name} />"
        
        if "</body>" in content:
            content = content.replace("</body>", f"{usage_stmt}\n      </body>")
        else:
            # Fallback: append to end of main div or similar? 
            # If no body tag (e.g. inner layout), this might be tricky.
            # Assuming root layout has html/body.
            pass
            
        layout_file["content"] = content

    def _to_pascal_case(self, snake_str: str) -> str:
        return "".join(x.capitalize() for x in snake_str.lower().split("-"))
