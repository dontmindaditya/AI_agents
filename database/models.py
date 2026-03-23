"""
Database Models for Alembic Migrations

This module defines SQLAlchemy models that mirror the Pydantic models
used in the application. These models are used for Alembic migrations
to create and modify database tables.

Tables:
    - agent_categories: Categories for organizing agents
    - agents: Agent catalog with all agent metadata
    - agent_installations: Track which agents are installed in projects
    - projects: User projects for code generation
    - project_files: Files generated within projects
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, ForeignKey, 
    JSON, Integer, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


def generate_uuid():
    return str(uuid4())


class AgentCategory(Base):
    """Category for organizing agents in the marketplace."""
    __tablename__ = "agent_categories"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)
    icon_url = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    agents = relationship("Agent", back_populates="category")
    
    def __repr__(self):
        return f"<AgentCategory(name='{self.name}', slug='{self.slug}')>"


class Agent(Base):
    """Agent catalog entry with metadata and configuration."""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(String(1000), nullable=False)
    detailed_description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)
    pricing_tier = Column(String(50), default='free', index=True)
    
    # Category relationship
    category_id = Column(UUID(as_uuid=False), ForeignKey("agent_categories.id"), nullable=True)
    category = relationship("AgentCategory", back_populates="agents")
    
    # Agent code/configuration
    config_schema = Column(JSON, default=dict)
    dependencies = Column(JSON, default=dict)
    env_vars = Column(JSON, default=list)
    
    # UI Components
    frontend_component_code = Column(Text, nullable=True)
    backend_api_code = Column(Text, nullable=True)
    
    # Extra data (renamed from metadata to avoid SQLAlchemy conflict)
    extra_data = Column(JSON, default=dict)
    is_active = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_agents_pricing_active', 'pricing_tier', 'is_active'),
    )
    
    installations = relationship("AgentInstallation", back_populates="agent")
    
    def __repr__(self):
        return f"<Agent(name='{self.name}', slug='{self.slug}')>"


class Project(Base):
    """User project for code generation."""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Project configuration
    project_type = Column(String(50), nullable=True)  # frontend, backend, fullstack
    framework = Column(String(100), nullable=True)  # react, vue, next, etc.
    design_preferences = Column(JSON, default=dict)
    additional_context = Column(JSON, default=dict)
    
    # Status
    status = Column(String(50), default='pending', index=True)  # pending, in_progress, completed, failed
    current_stage = Column(String(50), nullable=True)
    
    # Results
    generated_files = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Files relationship
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")
    installations = relationship("AgentInstallation", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(name='{self.name}', status='{self.status}')>"


class ProjectFile(Base):
    """File generated within a project."""
    __tablename__ = "project_files"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    project = relationship("Project", back_populates="files")
    
    # File information
    file_path = Column(String(1000), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)  # component, page, api, config, etc.
    
    # Content
    content = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)  # javascript, typescript, python, etc.
    
    # File metadata
    size_bytes = Column(Integer, nullable=True)
    line_count = Column(Integer, nullable=True)
    extra_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('ix_project_files_project_path', 'project_id', 'file_path', unique=True),
    )
    
    def __repr__(self):
        return f"<ProjectFile(path='{self.file_path}')>"


class AgentInstallation(Base):
    """Track which agents are installed in which projects."""
    __tablename__ = "agent_installations"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    agent = relationship("Agent", back_populates="installations")
    
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    project = relationship("Project", back_populates="installations")
    
    # Installation configuration
    config = Column(JSON, default=dict)
    env_values = Column(JSON, default=dict)  # Sensitive values stored separately
    
    # Status
    is_enabled = Column(Boolean, default=True)
    installed_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('agent_id', 'project_id', name='uq_agent_project'),
        Index('ix_agent_installations_project_enabled', 'project_id', 'is_enabled'),
    )
    
    def __repr__(self):
        return f"<AgentInstallation(agent_id='{self.agent_id}', project_id='{self.project_id}')>"


class MigrationHistory(Base):
    """Track migration history for debugging."""
    __tablename__ = "migration_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), nullable=False, unique=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(Text, nullable=True)
