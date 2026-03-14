"""
Agent Registry - Auto-discovers all agents in the agents directory

This module provides automatic discovery and registration of agents.
It scans the agents directory for valid agent implementations and
makes them available through a central registry.

The registry:
- Automatically discovers agents on startup
- Caches agent classes and metadata
- Provides lookup by agent ID
- Supports dynamic loading of agent modules

Usage:
    from agents.registry import agent_registry
    
    # Get all available agents
    agents = agent_registry.get_all_agents()
    
    # Get specific agent
    agent_class = agent_registry.get_agent_class("frontend")
    
    # Get agent metadata
    metadata = agent_registry.get_agent_metadata("frontend")
"""

import os
import importlib.util
import inspect
import sys
from typing import List, Dict, Any, Optional, Type
from pathlib import Path
from .base import BaseAgent, AgentMetadata


class AgentRegistry:
    """
    Registry for all available agents.
    
    This class auto-discovers agents from the agents directory and
    provides methods to query them. It uses lazy loading to only
    instantiate agents when needed.
    
    Attributes:
        agents_dir: Path to the agents directory
        _agents_cache: Cache of agent classes by ID
        _metadata_cache: Cache of agent metadata by ID
    
    Example:
        >>> registry = AgentRegistry()
        >>> agents = registry.get_all_agents()
        >>> print([a['name'] for a in agents])
        ['Frontend Agent', 'Backend Agent', ...]
    """
    
    def __init__(self):
        """
        Initialize the registry and discover all agents.
        """
        self.agents_dir = Path(__file__).parent
        self._agents_cache: Dict[str, Type[BaseAgent]] = {}
        self._metadata_cache: Dict[str, AgentMetadata] = {}
        self.discover_agents()
    
    def discover_agents(self) -> None:
        """
        Scan agents directory for subdirectories containing valid agents.
        
        An agent is valid if it has a Python file (agent.py, main.py, or __init__.py)
        that exports a class inheriting from BaseAgent.
        
        The method clears existing caches before scanning.
        """
        self._agents_cache.clear()
        self._metadata_cache.clear()
        
        print(f"Scanning for agents in {self.agents_dir}...")
        
        # Iterate over all subdirectories in agents/
        for item in self.agents_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_') and not item.name.startswith('.'):
                self._load_agent_from_dir(item)

    def _load_agent_from_dir(self, agent_dir: Path) -> None:
        """
        Try to load an agent from a specific directory.
        
        Looks for agent.py, main.py, or __init__.py files in the
        agent directory and loads any class that inherits from BaseAgent.
        
        Args:
            agent_dir: Path to the agent directory
        """
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
                        
                        try:
                            instance = obj()
                            metadata = instance.metadata
                            
                            agent_id = agent_dir.name
                            
                            self._agents_cache[agent_id] = obj
                            self._metadata_cache[agent_id] = metadata
                            print(f"[INFO] Loaded agent: {metadata.name} ({agent_id})")
                            return
                        except Exception as e:
                            print(f"[WARN] Could not load agent in {agent_dir}: {e}")

        except Exception as e:
            print(f"[ERROR] Error loading module {module_name}: {e}")

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        Get list of all available agents with their metadata.
        
        Returns:
            List of agent info dictionaries sorted by name.
            Each dictionary contains the agent's metadata plus its ID.
        """
        agents = []
        for agent_id, metadata in self._metadata_cache.items():
            info = metadata.model_dump()
            info['id'] = agent_id
            agents.append(info)
        return sorted(agents, key=lambda x: x.get('name', ''))
    
    def get_agent_class(self, agent_id: str) -> Optional[Type[BaseAgent]]:
        """
        Get the agent class by ID.
        
        Args:
            agent_id: The unique identifier of the agent (folder name)
            
        Returns:
            The agent class if found, None otherwise.
        """
        return self._agents_cache.get(agent_id)
    
    def get_agent_metadata(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific agent.
        
        Args:
            agent_id: The unique identifier of the agent
            
        Returns:
            Dictionary containing agent metadata plus ID, or None if not found.
        """
        meta = self._metadata_cache.get(agent_id)
        if meta:
            data = meta.model_dump()
            data['id'] = agent_id
            return data
        return None


# Global registry instance
agent_registry = AgentRegistry()
