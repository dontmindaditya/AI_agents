from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

# Shared Models

class AgentCategory(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class AgentBase(BaseModel):
    name: str
    description: str
    detailed_description: Optional[str] = None
    icon_url: Optional[str] = None
    pricing_tier: str = 'free'
    metadata: Dict[str, Any] = {}

class AgentSchema(AgentBase):
    id: UUID
    slug: str
    category_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Include these only when needed details are requested? 
    # For list view we might omit them, but keeping it simple for now.
    config_schema: Dict[str, Any] = {}
    dependencies: Dict[str, str] = {}
    
    class Config:
        from_attributes = True

class AgentDetail(AgentSchema):
    frontend_component_code: Optional[str] = None
    backend_api_code: Optional[str] = None
    env_vars: List[Dict[str, str]] = []

# Request Models

class AgentCreateRequest(AgentBase):
    slug: Optional[str] = None # Can be auto-generated
    category_id: UUID
    frontend_component_code: str
    backend_api_code: Optional[str] = None
    dependencies: Dict[str, str] = {}
    env_vars: List[Dict[str, str]] = []
    config_schema: Dict[str, Any] = {}
    is_active: bool = False

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    icon_url: Optional[str] = None
    pricing_tier: Optional[str] = None
    category_id: Optional[UUID] = None
    frontend_component_code: Optional[str] = None
    backend_api_code: Optional[str] = None
    dependencies: Optional[Dict[str, str]] = None
    env_vars: Optional[List[Dict[str, str]]] = None
    config_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class ProjectAgentInstallRequest(BaseModel):
    agent_id: UUID
    config: Dict[str, Any] = {}

class ProjectAgentUpdateRequest(BaseModel):
    config: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None

# Response Models

class ProjectAgentResponse(BaseModel):
    id: UUID
    project_id: str
    agent_id: UUID
    agent: Optional[AgentSchema] = None # Expanded agent details
    config: Dict[str, Any]
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
