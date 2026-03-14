"""
Generation Stage

This stage generates the actual code for the project based on the plan created
in the planning stage. It uses the FrontendAdapter to invoke the frontend agent
which generates:
- React/Vue/Angular components
- Styling (CSS/Tailwind)
- Configuration files
- Supporting utilities

The generation stage runs after planning and analysis complete.

Usage:
    stage = GenerationStage(ws_manager)
    result = await stage.execute("project-123", context)
"""

from typing import Dict, Any, List
from pipeline.adapters import FrontendAdapter
from services.code_generator import CodeGenerator
from services.websocket_manager import WebSocketManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GenerationStage:
    """
    Generation stage that produces project code files.
    
    This stage takes the project plan and generates actual code files including
    components, styles, and configuration. It supports multiple frameworks
    and uses AI agents for intelligent code generation.
    
    Attributes:
        ws_manager: WebSocket manager for real-time updates
        frontend_adapter: FrontendAdapter for code generation
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        """
        Initialize the generation stage.
        
        Args:
            websocket_manager: WebSocket manager for sending updates
        """
        self.ws_manager = websocket_manager
        self.frontend_adapter = FrontendAdapter()
    
    async def execute(self, project_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the generation stage for a project.
        
        Args:
            project_id: Unique project identifier
            context: Pipeline context containing:
                - project_data: Project configuration
                    - description: Project description
                    - framework: Target framework (react, vue, etc.)
                    - design_preferences: UI/UX preferences
                    
        Returns:
            Dictionary containing generated files and status
        """
        try:
            project_data = context["project_data"]
            description = project_data.get("description", "website")
            framework = project_data.get("framework", "react")
            
            all_files = []
            
            # Generate frontend using user's frontend_agent
            logger.info(f"Generating frontend for: {description}")
            result = self.frontend_adapter.generate_components(description, framework)
            
            if result["success"]:
                all_files.extend(result["files"])
                logger.info(f"Generated {len(result['files'])} frontend files")
            else:
                logger.warning(f"Frontend generation had issues: {result.get('error')}")
                # Add fallback file
                all_files.append({
                    "path": "src/App.tsx",
                    "content": f"// Generated for: {description}\nexport default function App() {{\n  return <div>Hello World</div>\n}}",
                    "type": "component"
                })
            
            # Generate config files
            config_files = self._generate_config_files(framework, context.get("plan", {}))
            all_files.extend(config_files)
            
            context["all_files"] = all_files
            
            logger.info(f"Total files generated: {len(all_files)}")
            
            return {
                "files": all_files,
                "total_files": len(all_files)
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def _generate_config_files(self, framework: str, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate config files"""
        files = []
        
        # package.json
        files.append({
            "path": "package.json",
            "content": CodeGenerator.generate_package_json(framework),
            "type": "config"
        })
        
        # tsconfig.json
        files.append({
            "path": "tsconfig.json",
            "content": CodeGenerator.generate_tsconfig(framework),
            "type": "config"
        })
        
        # tailwind.config.js
        files.append({
            "path": "tailwind.config.js",
            "content": CodeGenerator.generate_tailwind_config(),
            "type": "config"
        })
        
        return files