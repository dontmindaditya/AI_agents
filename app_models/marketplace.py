from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
import re

# Shared Models

class AgentCategory(BaseModel):
    id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = Field(None, max_length=500)
    
    class Config:
        from_attributes = True

class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    detailed_description: Optional[str] = Field(None, max_length=5000)
    icon_url: Optional[str] = Field(None, max_length=500)
    pricing_tier: str = Field(default='free')
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('pricing_tier')
    @classmethod
    def validate_pricing_tier(cls, v: str) -> str:
        allowed = ['free', 'basic', 'pro', 'enterprise']
        if v.lower() not in allowed:
            raise ValueError(f'pricing_tier must be one of: {", ".join(allowed)}')
        return v.lower()
    
    @field_validator('icon_url')
    @classmethod
    def validate_icon_url(cls, v: Optional[str]) -> Optional[str]:
        if v and not (v.startswith('http://') or v.startswith('https://') or v.startswith('/')):
            raise ValueError('icon_url must be a valid URL or absolute path')
        return v

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
    slug: Optional[str] = Field(None, pattern=r"^[a-z0-9-]+$")
    category_id: UUID
    frontend_component_code: str = Field(..., max_length=50000)
    backend_api_code: Optional[str] = Field(None, max_length=50000)
    dependencies: Dict[str, str] = Field(default_factory=dict)
    env_vars: List[Dict[str, str]] = Field(default_factory=list, max_length=50)
    config_schema: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = False
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError('slug must contain only lowercase letters, numbers, and hyphens')
        return v

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    detailed_description: Optional[str] = Field(None, max_length=5000)
    icon_url: Optional[str] = Field(None, max_length=500)
    pricing_tier: Optional[str] = None
    category_id: Optional[UUID] = None
    frontend_component_code: Optional[str] = Field(None, max_length=50000)
    backend_api_code: Optional[str] = Field(None, max_length=50000)
    dependencies: Optional[Dict[str, str]] = None
    env_vars: Optional[List[Dict[str, str]]] = Field(None, max_length=50)
    config_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @field_validator('pricing_tier')
    @classmethod
    def validate_pricing_tier(cls, v: Optional[str]) -> Optional[str]:
        if v:
            allowed = ['free', 'basic', 'pro', 'enterprise']
            if v.lower() not in allowed:
                raise ValueError(f'pricing_tier must be one of: {", ".join(allowed)}')
            return v.lower()
        return v

class ProjectAgentInstallRequest(BaseModel):
    agent_id: UUID
    config: Dict[str, Any] = Field(default_factory=dict, max_length=100)
    
    @field_validator('config')
    @classmethod
    def validate_config(cls, v: Dict) -> Dict:
        if not isinstance(v, dict):
            raise ValueError('config must be a dictionary')
        return v

class ProjectAgentUpdateRequest(BaseModel):
    config: Optional[Dict[str, Any]] = Field(None, max_length=100)
    is_enabled: Optional[bool] = None
    
    @field_validator('config')
    @classmethod
    def validate_config(cls, v: Optional[Dict]) -> Optional[Dict]:
        if v is not None and not isinstance(v, dict):
            raise ValueError('config must be a dictionary')
        return v
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
