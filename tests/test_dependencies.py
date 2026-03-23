"""
Tests for Dependency Injection Module
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))


class TestDependencyInjection:
    """Tests for dependency injection system."""

    def test_init_services(self):
        """Test service initialization."""
        from dependencies import init_services, get_ws_manager, get_orchestrator, reset_services
        
        reset_services()
        
        mock_ws = MagicMock()
        mock_orch = MagicMock()
        
        init_services(mock_ws, mock_orch)
        
        assert get_ws_manager() == mock_ws
        assert get_orchestrator() == mock_orch

    def test_reset_services(self):
        """Test service reset."""
        from dependencies import init_services, reset_services, get_ws_manager, get_orchestrator
        
        mock_ws = MagicMock()
        mock_orch = MagicMock()
        
        init_services(mock_ws, mock_orch)
        
        # Verify services are accessible
        assert get_ws_manager() == mock_ws
        assert get_orchestrator() == mock_orch
        
        reset_services()
        
        # Verify services raise after reset
        with pytest.raises(RuntimeError):
            get_ws_manager()
        
        with pytest.raises(RuntimeError):
            get_orchestrator()

    def test_get_ws_manager_raises_when_not_initialized(self):
        """Test that get_ws_manager raises when not initialized."""
        from dependencies import reset_services, get_ws_manager
        
        reset_services()
        
        with pytest.raises(RuntimeError) as exc_info:
            get_ws_manager()
        
        assert "not initialized" in str(exc_info.value)

    def test_get_orchestrator_raises_when_not_initialized(self):
        """Test that get_orchestrator raises when not initialized."""
        from dependencies import reset_services, get_orchestrator
        
        reset_services()
        
        with pytest.raises(RuntimeError) as exc_info:
            get_orchestrator()
        
        assert "not initialized" in str(exc_info.value)

    def test_get_optional_orchestrator_returns_none_when_not_initialized(self):
        """Test that optional orchestrator returns None when not initialized."""
        from dependencies import reset_services, get_optional_orchestrator
        
        reset_services()
        
        result = get_optional_orchestrator()
        assert result is None

    def test_get_optional_orchestrator_returns_instance_when_initialized(self):
        """Test that optional orchestrator returns instance when initialized."""
        from dependencies import init_services, get_optional_orchestrator, reset_services
        
        reset_services()
        
        mock_orch = MagicMock()
        init_services(MagicMock(), mock_orch)
        
        result = get_optional_orchestrator()
        assert result == mock_orch

    def test_supabase_client_initialization(self):
        """Test Supabase client can be passed to init_services."""
        from dependencies import init_services, get_supabase_client, reset_services
        
        reset_services()
        
        mock_ws = MagicMock()
        mock_orch = MagicMock()
        mock_supabase = MagicMock()
        
        init_services(mock_ws, mock_orch, mock_supabase)
        
        assert get_supabase_client() == mock_supabase

    def test_supabase_client_defaults_to_none(self):
        """Test Supabase client defaults to None."""
        from dependencies import reset_services, get_supabase_client
        
        reset_services()
        
        assert get_supabase_client() is None


class TestDependencyInjectionWithFastAPI:
    """Tests for dependency injection integration with FastAPI."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        from dependencies import init_services, reset_services
        
        reset_services()
        
        mock_ws = MagicMock()
        mock_orch = MagicMock()
        mock_orch.get_active_pipeline_count.return_value = 5
        
        init_services(mock_ws, mock_orch)
        
        yield {"ws": mock_ws, "orch": mock_orch}
        
        reset_services()

    def test_dependency_injection_in_endpoint(self, mock_services):
        """Test that dependency injection works in endpoints."""
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient
        from dependencies import get_ws_manager, get_orchestrator
        
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint(
            ws_mgr = Depends(get_ws_manager),
            orch = Depends(get_orchestrator)
        ):
            return {
                "ws_count": len(ws_mgr.active_connections) if hasattr(ws_mgr, 'active_connections') else 0,
                "orch_pipelines": orch.get_active_pipeline_count()
            }
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["orch_pipelines"] == 5

    def test_health_endpoint_uses_di(self, mock_services):
        """Test health endpoint uses dependency injection."""
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient
        from dependencies import get_ws_manager, get_optional_orchestrator
        
        app = FastAPI()
        
        @app.get("/health")
        async def health(
            ws_mgr = Depends(get_ws_manager),
            orch = Depends(get_optional_orchestrator)
        ):
            return {
                "connections": len(ws_mgr.active_connections),
                "pipelines": orch.get_active_pipeline_count() if orch else 0
            }
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "connections" in response.json()
        assert "pipelines" in response.json()


class TestDependencyInjectionOverride:
    """Tests for overriding dependencies (useful for testing)."""

    def test_override_get_ws_manager(self):
        """Test that we can override the dependency."""
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient
        from dependencies import get_ws_manager, reset_services
        
        reset_services()
        
        app = FastAPI()
        
        custom_ws = MagicMock()
        custom_ws.custom_attr = "custom_value"
        
        def override_get_ws():
            return custom_ws
        
        app.dependency_overrides[get_ws_manager] = override_get_ws
        
        @app.get("/test")
        async def test_endpoint(ws = Depends(get_ws_manager)):
            return {"has_custom": hasattr(ws, 'custom_attr'), "value": ws.custom_attr}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert response.json()["has_custom"] is True
        assert response.json()["value"] == "custom_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
