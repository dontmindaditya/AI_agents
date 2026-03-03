"""
Adapter for Frontend Agent
Bridges pipeline to user's frontend_agent implementation
"""
import sys
import os

# Add frontend_agent to Python path
frontend_agent_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'agents', 'frontend_agent')
sys.path.insert(0, frontend_agent_dir)

try:
    from graph.frontend_graph import create_frontend_graph
    FRONTEND_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import frontend_graph: {e}")
    FRONTEND_AVAILABLE = False
    create_frontend_graph = None


class FrontendAdapter:
    """Adapter for frontend_agent"""
    
    def __init__(self):
        if FRONTEND_AVAILABLE:
            self.graph = create_frontend_graph()
        else:
            self.graph = None
    
    def generate_components(self, description: str, framework: str = "react") -> dict:
        """Generate frontend components"""
        if not self.graph:
            # Fallback if agent not available
            fallback_code = f"""// Generated for: {description}
import React from 'react';

export default function App() {{
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          {description}
        </h1>
        <p className="text-lg text-gray-600">
          This is a generated landing page. Frontend agent integration in progress.
        </p>
      </div>
    </div>
  );
}}"""
            
            return {
                "files": [{
                    "path": "src/App.tsx",
                    "content": fallback_code,
                    "type": "component"
                }],
                "success": True,
                "fallback": True
            }
        
        user_input = description
        
        try:
            final_state = self.graph.run(user_input=user_input, framework=framework)
            
            generated_code = final_state.get("optimized_code") or final_state.get("generated_code")
            
            # Convert to file structure
            files = []
            if generated_code:
                files.append({
                    "path": "src/App.tsx",
                    "content": generated_code,
                    "type": "component"
                })
            
            return {
                "files": files,
                "state": final_state,
                "success": bool(generated_code)
            }
        except Exception as e:
            return {
                "files": [],
                "error": str(e),
                "success": False
            }
