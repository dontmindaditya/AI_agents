"""
Test suite for marketplace models.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

import pytest
from uuid import uuid4
from pydantic import ValidationError
from app_models.marketplace import (
    AgentCategory,
    AgentBase,
    AgentCreateRequest,
    AgentUpdateRequest,
    ProjectAgentInstallRequest,
    ProjectAgentUpdateRequest
)


class TestAgentCategory:
    """Tests for AgentCategory model."""

    def test_valid_category(self):
        """Test creating a valid AgentCategory."""
        category = AgentCategory(
            id=uuid4(),
            name="Frontend Agents",
            slug="frontend-agents",
            description="Agents for frontend development"
        )
        
        assert category.name == "Frontend Agents"
        assert category.slug == "frontend-agents"

    def test_invalid_slug(self):
        """Test that invalid slug format is rejected."""
        with pytest.raises(ValidationError):
            AgentCategory(
                id=uuid4(),
                name="Test",
                slug="Invalid Slug!",  # Contains spaces and uppercase
                description="Test"
            )

    def test_valid_slug_formats(self):
        """Test valid slug formats."""
        valid_slugs = ["frontend", "backend-agent", "my-agent-123"]
        
        for slug in valid_slugs:
            category = AgentCategory(
                id=uuid4(),
                name="Test",
                slug=slug
            )
            assert category.slug == slug


class TestAgentBase:
    """Tests for AgentBase model."""

    def test_valid_agent(self):
        """Test creating a valid AgentBase."""
        agent = AgentBase(
            name="Frontend Agent",
            description="Generates React code",
            pricing_tier="free"
        )
        
        assert agent.name == "Frontend Agent"
        assert agent.pricing_tier == "free"

    def test_invalid_pricing_tier(self):
        """Test that invalid pricing_tier is rejected."""
        with pytest.raises(ValidationError):
            AgentBase(
                name="Test",
                description="Test",
                pricing_tier="invalid"  # Not in allowed list
            )

    def test_valid_pricing_tiers(self):
        """Test all valid pricing tiers."""
        for tier in ["free", "basic", "pro", "enterprise"]:
            agent = AgentBase(
                name="Test",
                description="Test",
                pricing_tier=tier
            )
            assert agent.pricing_tier == tier

    def test_invalid_icon_url(self):
        """Test that invalid icon_url is rejected."""
        with pytest.raises(ValidationError):
            AgentBase(
                name="Test",
                description="Test",
                icon_url="not-a-valid-url"  # Not http/https/path
            )


class TestAgentCreateRequest:
    """Tests for AgentCreateRequest model."""

    def test_valid_request(self):
        """Test creating a valid AgentCreateRequest."""
        request = AgentCreateRequest(
            name="Test Agent",
            description="A test agent",
            category_id=uuid4(),
            frontend_component_code="export default function() {}"
        )
        
        assert request.name == "Test Agent"
        assert request.is_active == False  # Default

    def test_valid_slug(self):
        """Test valid slug format."""
        request = AgentCreateRequest(
            name="Test Agent",
            description="Test",
            category_id=uuid4(),
            slug="my-test-agent",
            frontend_component_code="code"
        )
        assert request.slug == "my-test-agent"

    def test_invalid_slug(self):
        """Test that invalid slug is rejected."""
        with pytest.raises(ValidationError):
            AgentCreateRequest(
                name="Test",
                description="Test",
                category_id=uuid4(),
                slug="Invalid Slug!",  # Invalid format
                frontend_component_code="code"
            )

    def test_max_code_length(self):
        """Test that code exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            AgentCreateRequest(
                name="Test",
                description="Test",
                category_id=uuid4(),
                frontend_component_code="x" * 50001  # Exceeds max
            )

    def test_max_env_vars(self):
        """Test that too many env vars are rejected."""
        with pytest.raises(ValidationError):
            AgentCreateRequest(
                name="Test",
                description="Test",
                category_id=uuid4(),
                frontend_component_code="code",
                env_vars=[{"key": f"VAR{i}"} for i in range(51)]  # Exceeds max
            )


class TestAgentUpdateRequest:
    """Tests for AgentUpdateRequest model."""

    def test_partial_update(self):
        """Test that partial updates work."""
        request = AgentUpdateRequest(
            name="Updated Name"
        )
        
        assert request.name == "Updated Name"
        assert request.description is None

    def test_update_pricing_tier(self):
        """Test updating pricing_tier."""
        request = AgentUpdateRequest(pricing_tier="pro")
        assert request.pricing_tier == "pro"

    def test_invalid_pricing_tier_update(self):
        """Test that invalid pricing_tier in update is rejected."""
        with pytest.raises(ValidationError):
            AgentUpdateRequest(pricing_tier="super-premium")


class TestProjectAgentInstallRequest:
    """Tests for ProjectAgentInstallRequest model."""

    def test_valid_request(self):
        """Test creating a valid install request."""
        request = ProjectAgentInstallRequest(
            agent_id=uuid4(),
            config={"setting": "value"}
        )
        
        assert request.agent_id is not None
        assert request.config["setting"] == "value"

    def test_empty_config(self):
        """Test that empty config is allowed."""
        request = ProjectAgentInstallRequest(
            agent_id=uuid4()
        )
        assert request.config == {}


class TestProjectAgentUpdateRequest:
    """Tests for ProjectAgentUpdateRequest model."""

    def test_enable_agent(self):
        """Test enabling an agent."""
        request = ProjectAgentUpdateRequest(is_enabled=True)
        assert request.is_enabled == True

    def test_update_config(self):
        """Test updating agent config."""
        request = ProjectAgentUpdateRequest(config={"key": "value"})
        assert request.config["key"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
