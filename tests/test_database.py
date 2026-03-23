"""
Tests for Database Models

These tests verify that SQLAlchemy models are correctly defined
and can be used for Alembic migrations.
"""
import pytest
from datetime import datetime
from uuid import uuid4
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))


class TestDatabaseModels:
    """Tests for SQLAlchemy database models."""

    def test_agent_category_model(self):
        """Test AgentCategory model can be instantiated."""
        from database.models import AgentCategory
        
        category = AgentCategory(
            id=str(uuid4()),
            name="Test Category",
            slug="test-category",
            description="A test category"
        )
        
        assert category.name == "Test Category"
        assert category.slug == "test-category"
        assert category.description == "A test category"

    def test_agent_model(self):
        """Test Agent model can be instantiated."""
        from database.models import Agent
        
        agent = Agent(
            id=str(uuid4()),
            name="Test Agent",
            slug="test-agent",
            description="A test agent",
            pricing_tier="free",
            is_active=True
        )
        
        assert agent.name == "Test Agent"
        assert agent.slug == "test-agent"
        assert agent.pricing_tier == "free"
        assert agent.is_active is True

    def test_project_model(self):
        """Test Project model can be instantiated."""
        from database.models import Project
        
        project = Project(
            id=str(uuid4()),
            user_id="user-123",
            name="Test Project",
            status="pending"
        )
        
        assert project.name == "Test Project"
        assert project.user_id == "user-123"
        assert project.status == "pending"

    def test_project_file_model(self):
        """Test ProjectFile model can be instantiated."""
        from database.models import ProjectFile
        
        project_id = str(uuid4())
        file = ProjectFile(
            id=str(uuid4()),
            project_id=project_id,
            file_path="src/App.tsx",
            file_name="App.tsx",
            content="export default function App() {}",
            language="typescript"
        )
        
        assert file.file_path == "src/App.tsx"
        assert file.project_id == project_id
        assert file.language == "typescript"

    def test_agent_installation_model(self):
        """Test AgentInstallation model can be instantiated."""
        from database.models import AgentInstallation
        
        agent_id = str(uuid4())
        project_id = str(uuid4())
        
        installation = AgentInstallation(
            id=str(uuid4()),
            agent_id=agent_id,
            project_id=project_id,
            is_enabled=True
        )
        
        assert installation.agent_id == agent_id
        assert installation.project_id == project_id
        assert installation.is_enabled is True

    def test_models_have_table_names(self):
        """Test all models have table names defined."""
        from database.models import AgentCategory, Agent, Project, ProjectFile, AgentInstallation
        
        assert AgentCategory.__tablename__ == "agent_categories"
        assert Agent.__tablename__ == "agents"
        assert Project.__tablename__ == "projects"
        assert ProjectFile.__tablename__ == "project_files"
        assert AgentInstallation.__tablename__ == "agent_installations"

    def test_models_have_primary_keys(self):
        """Test all models have primary key columns."""
        from database.models import AgentCategory, Agent, Project, ProjectFile, AgentInstallation
        
        assert hasattr(AgentCategory, 'id')
        assert hasattr(Agent, 'id')
        assert hasattr(Project, 'id')
        assert hasattr(ProjectFile, 'id')
        assert hasattr(AgentInstallation, 'id')

    def test_models_have_timestamps(self):
        """Test relevant models have timestamp columns."""
        from database.models import Agent, Project, ProjectFile
        
        assert hasattr(Agent, 'created_at')
        assert hasattr(Agent, 'updated_at')
        assert hasattr(Project, 'created_at')
        assert hasattr(Project, 'updated_at')
        assert hasattr(ProjectFile, 'created_at')
        assert hasattr(ProjectFile, 'updated_at')

    def test_agent_has_foreign_key_to_category(self):
        """Test Agent model has foreign key to category."""
        from database.models import Agent
        
        assert hasattr(Agent, 'category_id')
        
        foreign_keys = [fk for fk in Agent.__table__.foreign_keys]
        assert any('agent_categories' in str(fk) for fk in foreign_keys)

    def test_project_file_has_foreign_key_to_project(self):
        """Test ProjectFile model has foreign key to project."""
        from database.models import ProjectFile
        
        assert hasattr(ProjectFile, 'project_id')
        
        foreign_keys = [fk for fk in ProjectFile.__table__.foreign_keys]
        assert any('projects' in str(fk) for fk in foreign_keys)

    def test_agent_installation_has_composite_unique_constraint(self):
        """Test AgentInstallation has unique constraint on agent_id + project_id."""
        from database.models import AgentInstallation
        
        unique_constraints = [uc for uc in AgentInstallation.__table__.constraints 
                            if hasattr(uc, 'columns')]
        
        has_composite = any(
            len(uc.columns) == 2 and 
            any(c.name == 'agent_id' for c in uc.columns) and
            any(c.name == 'project_id' for c in uc.columns)
            for uc in unique_constraints
        )
        
        assert has_composite, "AgentInstallation should have unique constraint on (agent_id, project_id)"

    def test_json_columns_exist(self):
        """Test models have JSON columns for flexible data."""
        from database.models import Agent, Project, ProjectFile
        
        assert hasattr(Agent, 'config_schema')
        assert hasattr(Agent, 'extra_data')
        assert hasattr(Project, 'design_preferences')
        assert hasattr(ProjectFile, 'extra_data')


class TestMigrationScript:
    """Tests for migration script generation."""

    def test_initial_migration_exists(self):
        """Test initial migration file exists."""
        migration_path = Path(__file__).parent.parent / "alembic" / "versions" / "001_initial.py"
        assert migration_path.exists(), "Initial migration file should exist"

    def test_initial_migration_has_upgrade(self):
        """Test initial migration has upgrade function."""
        migration_path = Path(__file__).parent.parent / "alembic" / "versions" / "001_initial.py"
        
        assert migration_path.exists()
        
        content = migration_path.read_text()
        assert "def upgrade()" in content
        assert "def downgrade()" in content
        assert "agent_categories" in content
        assert "agents" in content
        assert "projects" in content


class TestMigrationManagement:
    """Tests for migration management utilities."""

    def test_run_migrations_function_exists(self):
        """Test run_migrations function exists."""
        from database.migrations import run_migrations
        
        assert callable(run_migrations)

    def test_create_migration_function_exists(self):
        """Test create_migration function exists."""
        from database.migrations import create_migration
        
        assert callable(create_migration)

    def test_rollback_migration_function_exists(self):
        """Test rollback_migration function exists."""
        from database.migrations import rollback_migration
        
        assert callable(rollback_migration)

    def test_show_current_version_function_exists(self):
        """Test show_current_version function exists."""
        from database.migrations import show_current_version
        
        assert callable(show_current_version)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
