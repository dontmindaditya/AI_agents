"""Initial schema - AgentHub tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-23

This migration creates the initial schema for AgentHub including:
- agent_categories: Categories for organizing agents
- agents: Agent catalog with metadata and configuration
- projects: User projects for code generation
- project_files: Files generated within projects
- agent_installations: Track agent installations in projects
- migration_history: Track migration history
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create agent_categories table
    op.create_table(
        'agent_categories',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('sort_order', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_agent_categories_slug', 'agent_categories', ['slug'])
    
    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False, unique=True),
        sa.Column('description', sa.String(1000), nullable=False),
        sa.Column('detailed_description', sa.Text, nullable=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('pricing_tier', sa.String(50), default='free'),
        sa.Column('category_id', postgresql.UUID(as_uuid=False), sa.ForeignKey('agent_categories.id'), nullable=True),
        sa.Column('config_schema', postgresql.JSON, default=dict),
        sa.Column('dependencies', postgresql.JSON, default=dict),
        sa.Column('env_vars', postgresql.JSON, default=list),
        sa.Column('frontend_component_code', sa.Text, nullable=True),
        sa.Column('backend_api_code', sa.Text, nullable=True),
        sa.Column('extra_data', postgresql.JSON, default=dict),
        sa.Column('is_active', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_agents_slug', 'agents', ['slug'])
    op.create_index('ix_agents_pricing_tier', 'agents', ['pricing_tier'])
    op.create_index('ix_agents_is_active', 'agents', ['is_active'])
    op.create_index('ix_agents_pricing_active', 'agents', ['pricing_tier', 'is_active'])
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('project_type', sa.String(50), nullable=True),
        sa.Column('framework', sa.String(100), nullable=True),
        sa.Column('design_preferences', postgresql.JSON, default=dict),
        sa.Column('additional_context', postgresql.JSON, default=dict),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('current_stage', sa.String(50), nullable=True),
        sa.Column('generated_files', sa.Integer, default=0),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])
    op.create_index('ix_projects_status', 'projects', ['status'])
    
    # Create project_files table
    op.create_table(
        'project_files',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=False), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('language', sa.String(50), nullable=True),
        sa.Column('size_bytes', sa.Integer, nullable=True),
        sa.Column('line_count', sa.Integer, nullable=True),
        sa.Column('extra_data', postgresql.JSON, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_project_files_file_path', 'project_files', ['file_path'])
    op.create_index('ix_project_files_project_path', 'project_files', ['project_id', 'file_path'], unique=True)
    
    # Create agent_installations table
    op.create_table(
        'agent_installations',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column('agent_id', postgresql.UUID(as_uuid=False), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=False), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('config', postgresql.JSON, default=dict),
        sa.Column('env_values', postgresql.JSON, default=dict),
        sa.Column('is_enabled', sa.Boolean, default=True),
        sa.Column('installed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_unique_constraint('uq_agent_project', 'agent_installations', ['agent_id', 'project_id'])
    op.create_index('ix_agent_installations_project_enabled', 'agent_installations', ['project_id', 'is_enabled'])
    
    # Create migration_history table
    op.create_table(
        'migration_history',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('version', sa.String(50), nullable=False, unique=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('description', sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('migration_history')
    op.drop_table('agent_installations')
    op.drop_table('project_files')
    op.drop_table('projects')
    op.drop_table('agents')
    op.drop_table('agent_categories')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
