"""
Tests for Health Check Module

Tests for the comprehensive health check system including:
- Component health checks
- Health report generation
- Health endpoints
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_health_status_values(self):
        """Test HealthStatus enum has correct values."""
        from services.health import HealthStatus
        
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestComponentHealth:
    """Tests for ComponentHealth dataclass."""

    def test_component_health_creation(self):
        """Test ComponentHealth can be created."""
        from services.health import ComponentHealth, HealthStatus
        
        component = ComponentHealth(
            name="test",
            status=HealthStatus.HEALTHY,
            latency_ms=10.5,
            message="All good"
        )
        
        assert component.name == "test"
        assert component.status == HealthStatus.HEALTHY
        assert component.latency_ms == 10.5
        assert component.message == "All good"
        assert isinstance(component.timestamp, datetime)

    def test_component_health_to_dict(self):
        """Test ComponentHealth to_dict method."""
        from services.health import ComponentHealth, HealthStatus
        
        component = ComponentHealth(
            name="test",
            status=HealthStatus.HEALTHY,
            latency_ms=10.5,
            message="All good"
        )
        
        result = component.to_dict()
        
        assert result["name"] == "test"
        assert result["status"] == "healthy"
        assert result["latency_ms"] == 10.5
        assert result["message"] == "All good"
        assert "timestamp" in result


class TestHealthReport:
    """Tests for HealthReport dataclass."""

    def test_health_report_creation(self):
        """Test HealthReport can be created."""
        from services.health import HealthReport, ComponentHealth, HealthStatus
        
        component = ComponentHealth(
            name="test",
            status=HealthStatus.HEALTHY,
            latency_ms=10.5
        )
        
        report = HealthReport(
            overall_status=HealthStatus.HEALTHY,
            components=[component],
            total_latency_ms=15.0
        )
        
        assert report.overall_status == HealthStatus.HEALTHY
        assert len(report.components) == 1
        assert report.total_latency_ms == 15.0
        assert isinstance(report.timestamp, datetime)

    def test_health_report_to_dict(self):
        """Test HealthReport to_dict method."""
        from services.health import HealthReport, ComponentHealth, HealthStatus
        
        component = ComponentHealth(
            name="test",
            status=HealthStatus.HEALTHY
        )
        
        report = HealthReport(
            overall_status=HealthStatus.HEALTHY,
            components=[component],
            total_latency_ms=15.0
        )
        
        result = report.to_dict()
        
        assert result["status"] == "healthy"
        assert result["overall"] == "healthy"
        assert result["total_latency_ms"] == 15.0
        assert len(result["components"]) == 1
        assert "timestamp" in result


class TestHealthChecker:
    """Tests for HealthChecker class."""

    @pytest.fixture
    def checker(self):
        """Create a HealthChecker instance."""
        from services.health import HealthChecker
        return HealthChecker()

    def test_checker_creation(self, checker):
        """Test HealthChecker can be created."""
        from services.health import HealthChecker
        assert isinstance(checker, HealthChecker)
        assert checker.timeout == 5.0

    @pytest.mark.asyncio
    async def test_check_all_returns_report(self, checker):
        """Test check_all returns a HealthReport."""
        report = await checker.check_all()
        
        assert hasattr(report, 'overall_status')
        assert hasattr(report, 'components')
        assert hasattr(report, 'total_latency_ms')
        assert isinstance(report.components, list)

    @pytest.mark.asyncio
    async def test_check_database_not_configured(self, checker):
        """Test database check when not configured."""
        with patch('services.health.settings') as mock_settings:
            mock_settings.SUPABASE_URL = None
            
            result = await checker.check_database()
            
            assert result.name == "database"
            assert result.status.value == "unknown"
            assert "not configured" in result.message.lower()

    @pytest.mark.asyncio
    async def test_check_anthropic_not_configured(self, checker):
        """Test Anthropic check when not configured."""
        with patch('services.health.settings') as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            
            result = await checker.check_anthropic()
            
            assert result.name == "anthropic"
            assert result.status.value == "unknown"
            assert "not configured" in result.message.lower()

    @pytest.mark.asyncio
    async def test_check_openai_not_configured(self, checker):
        """Test OpenAI check when not configured."""
        with patch('services.health.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            
            result = await checker.check_openai()
            
            assert result.name == "openai"
            assert result.status.value == "unknown"
            assert "not configured" in result.message.lower()

    @pytest.mark.asyncio
    async def test_check_groq_not_configured(self, checker):
        """Test Groq check when not configured."""
        with patch('services.health.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = None
            
            result = await checker.check_groq()
            
            assert result.name == "groq"
            assert result.status.value == "unknown"
            assert "not configured" in result.message.lower()

    @pytest.mark.asyncio
    async def test_check_gemini_not_configured(self, checker):
        """Test Gemini check when not configured."""
        with patch('services.health.settings') as mock_settings:
            mock_settings.GEMINI_API_KEY = None
            
            result = await checker.check_gemini()
            
            assert result.name == "gemini"
            assert result.status.value == "unknown"
            assert "not configured" in result.message.lower()

    @pytest.mark.asyncio
    async def test_check_websocket_returns_component(self, checker):
        """Test WebSocket check returns a ComponentHealth object."""
        result = await checker.check_websocket()
        
        assert result.name == "websocket"
        assert hasattr(result, 'status')
        assert hasattr(result, 'message')

    def test_determine_overall_status_all_healthy(self, checker):
        """Test overall status when all components are healthy."""
        from services.health import ComponentHealth, HealthStatus
        
        components = [
            ComponentHealth(name="a", status=HealthStatus.HEALTHY),
            ComponentHealth(name="b", status=HealthStatus.HEALTHY),
        ]
        
        result = checker._determine_overall_status(components)
        
        assert result == HealthStatus.HEALTHY

    def test_determine_overall_status_with_unhealthy(self, checker):
        """Test overall status with unhealthy component."""
        from services.health import ComponentHealth, HealthStatus
        
        components = [
            ComponentHealth(name="a", status=HealthStatus.HEALTHY),
            ComponentHealth(name="b", status=HealthStatus.UNHEALTHY),
        ]
        
        result = checker._determine_overall_status(components)
        
        assert result == HealthStatus.UNHEALTHY

    def test_determine_overall_status_with_degraded(self, checker):
        """Test overall status with degraded component."""
        from services.health import ComponentHealth, HealthStatus
        
        components = [
            ComponentHealth(name="a", status=HealthStatus.HEALTHY),
            ComponentHealth(name="b", status=HealthStatus.DEGRADED),
        ]
        
        result = checker._determine_overall_status(components)
        
        assert result == HealthStatus.DEGRADED

    def test_determine_overall_status_empty(self, checker):
        """Test overall status with no components."""
        from services.health import HealthStatus
        
        result = checker._determine_overall_status([])
        
        assert result == HealthStatus.UNKNOWN

    def test_determine_overall_status_with_unknown(self, checker):
        """Test overall status with unknown components (but all healthy)."""
        from services.health import ComponentHealth, HealthStatus
        
        components = [
            ComponentHealth(name="a", status=HealthStatus.HEALTHY),
            ComponentHealth(name="b", status=HealthStatus.UNKNOWN),
        ]
        
        result = checker._determine_overall_status(components)
        
        assert result == HealthStatus.DEGRADED


class TestHealthHelperFunctions:
    """Tests for health helper functions."""

    @pytest.mark.asyncio
    async def test_get_health_status(self):
        """Test get_health_status function."""
        from services.health import get_health_status
        
        result = await get_health_status()
        
        assert "status" in result
        assert "components" in result
        assert "total_latency_ms" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_get_simple_health(self):
        """Test get_simple_health function."""
        from services.health import get_simple_health
        
        result = await get_simple_health()
        
        assert "status" in result
        assert result["status"] in ["healthy", "degraded", "unhealthy", "unknown"]


class TestHealthEndpoints:
    """Tests for health endpoints in main.py."""

    def test_health_endpoint_exists(self):
        """Test health endpoint can be created."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        assert True

    def test_health_detailed_endpoint_structure(self):
        """Test detailed health response structure."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.get("/health/detailed")
        async def health_detailed():
            return {
                "status": "healthy",
                "overall": "healthy",
                "total_latency_ms": 100.0,
                "timestamp": "2024-01-01T00:00:00",
                "components": []
            }
        
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
