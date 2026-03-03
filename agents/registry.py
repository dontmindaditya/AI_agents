"""
Agent Registry - Auto-discovers all agents in the agents directory
"""
import os
import importlib.util
import inspect
import sys
from typing import List, Dict, Any, Optional, Type
from pathlib import Path
from .base import BaseAgent, AgentMetadata

class AgentRegistry:
    """Registry for all available agents"""
    
    def __init__(self):
        self.agents_dir = Path(__file__).parent
        self._agents_cache: Dict[str, Type[BaseAgent]] = {}
        self._metadata_cache: Dict[str, AgentMetadata] = {}
        self.discover_agents()
    
    def discover_agents(self) -> None:
        """
        Scan agents directory for subdirectories containing valid agents.
        An agent is valid if it has a python file exporting a class inheriting from BaseAgent.
        """
        self._agents_cache.clear()
        self._metadata_cache.clear()
        
        print(f"Scanning for agents in {self.agents_dir}...")
        
        # Iterate over all subdirectories in agents/
        for item in self.agents_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_') and not item.name.startswith('.'):
                self._load_agent_from_dir(item)

    def _load_agent_from_dir(self, agent_dir: Path) -> None:
        """Try to load an agent from a specific directory"""
        # We look for agent.py by default, or we can scan all .py files
        # Let's enforce a convention: 'agent.py' or 'main.py' or '__init__.py'
        
        candidates = ['agent.py', 'main.py', '__init__.py']
        params_file = None
        
        for cand in candidates:
            if (agent_dir / cand).exists():
                params_file = agent_dir / cand
                break
        
        if not params_file:
            return

        module_name = f"agents.{agent_dir.name}.{params_file.stem}"
        
        try:
            # Dynamic import
            spec = importlib.util.spec_from_file_location(module_name, params_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # Find class inheriting from BaseAgent
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseAgent) and 
                        obj is not BaseAgent):
                        
                        # Instantiate to get metadata (or make metadata static)
                        # We instantiate momentarily to get the dynamic property 'metadata' 
                        # Ideally metadata should be a class property or static, but property is fine for now
                        try:
                            instance = obj()
                            metadata = instance.metadata
                            
                            agent_id = agent_dir.name # Use folder name as ID
                            
                            self._agents_cache[agent_id] = obj
                            self._metadata_cache[agent_id] = metadata
                            print(f"[INFO] Loaded agent: {metadata.name} ({agent_id})")
                            return # Only load one agent per directory
                        except Exception as e:
                            print(f"[WARN] Could not load agent in {agent_dir}: {e}")

        except Exception as e:
            print(f"[ERROR] Error loading module {module_name}: {e}")

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get list of all available agents with their metadata"""
        agents = []
        for agent_id, metadata in self._metadata_cache.items():
            info = metadata.model_dump()
            info['id'] = agent_id # Ensure ID is consistent with folder name
            agents.append(info)
        return sorted(agents, key=lambda x: x.get('name', ''))
    
    def get_agent_class(self, agent_id: str) -> Optional[Type[BaseAgent]]:
        """Get the agent class by ID"""
        return self._agents_cache.get(agent_id)
    
    def get_agent_metadata(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for specific agent"""
        meta = self._metadata_cache.get(agent_id)
        if meta:
            data = meta.model_dump()
            data['id'] = agent_id
            return data
        return None

# Global registry instance
agent_registry = AgentRegistry()
