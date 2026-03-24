"""
Tests for Modular Configuration

Tests that verify the modular config system works correctly.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))


class TestAppSettings:
    """Tests for app configuration."""

    def test_app_name_default_or_from_env(self):
        """Test app name is set."""
        from config import settings
        assert settings.APP_NAME is not None
        assert len(settings.APP_NAME) > 0

    def test_app_version_default_or_from_env(self):
        """Test app version is set."""
        from config import settings
        assert settings.APP_VERSION is not None
        assert len(settings.APP_VERSION) > 0

    def test_server_defaults(self):
        """Test server default settings."""
        from config import settings
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert settings.WORKERS == 4

    def test_cors_origins_default(self):
        """Test CORS origins default list."""
        from config import settings
        assert "http://localhost:3000" in settings.CORS_ORIGINS


class TestAISettings:
    """Tests for AI configuration."""

    def test_ai_model_defaults(self):
        """Test default AI model settings."""
        from config import settings
        
        assert settings.CLAUDE_MODEL == "claude-sonnet-4-20250514"
        assert settings.GPT_MODEL == "gpt-4o"
        assert settings.GROQ_MODEL == "llama-3.1-70b-versatile"
        assert settings.GEMINI_MODEL == "gemini-1.5-pro"

    def test_ai_models_dict(self):
        """Test AI_MODELS configuration dict."""
        from config import AI_MODELS
        
        assert "claude" in AI_MODELS
        assert "gpt4" in AI_MODELS
        assert "groq" in AI_MODELS
        assert "gemini" in AI_MODELS

    def test_ai_model_structure(self):
        """Test AI model configuration structure."""
        from config import AI_MODELS
        
        for key, model_config in AI_MODELS.items():
            assert "provider" in model_config
            assert "model" in model_config
            assert "max_tokens" in model_config
            assert "temperature" in model_config
            assert "use_cases" in model_config


class TestAgentSettings:
    """Tests for agent configuration."""

    def test_agent_defaults(self):
        """Test default agent settings."""
        from config import settings
        
        assert settings.MAX_AGENTS == 10
        assert settings.AGENT_TIMEOUT == 300
        assert settings.MAX_RETRIES == 3

    def test_agent_configs_exist(self):
        """Test agent configs are defined."""
        from config import AGENT_CONFIGS
        
        assert "planner" in AGENT_CONFIGS
        assert "frontend" in AGENT_CONFIGS
        assert "backend" in AGENT_CONFIGS

    def test_agent_config_structure(self):
        """Test agent config structure."""
        from config import AGENT_CONFIGS
        
        for agent_id, config in AGENT_CONFIGS.items():
            assert "role" in config
            assert "goal" in config
            assert "model" in config
            assert "max_iterations" in config
            assert "allow_delegation" in config


class TestPipelineSettings:
    """Tests for pipeline configuration."""

    def test_pipeline_defaults(self):
        """Test default pipeline settings."""
        from config import settings
        
        assert settings.MAX_FILE_SIZE == 1024 * 1024
        assert settings.MAX_FILES_PER_PROJECT == 100

    def test_pipeline_stages_exist(self):
        """Test pipeline stages are defined."""
        from config import PIPELINE_STAGES
        
        assert "planning" in PIPELINE_STAGES
        assert "generation" in PIPELINE_STAGES
        assert "integration" in PIPELINE_STAGES

    def test_pipeline_stage_structure(self):
        """Test pipeline stage configuration structure."""
        from config import PIPELINE_STAGES
        
        for stage_id, stage_config in PIPELINE_STAGES.items():
            assert "order" in stage_config
            assert "name" in stage_config
            assert "agents" in stage_config
            assert "required" in stage_config
            assert "estimated_duration" in stage_config


class TestSecuritySettings:
    """Tests for security configuration."""

    def test_rate_limit_defaults(self):
        """Test default rate limit settings."""
        from config import settings
        
        assert settings.RATE_LIMIT_ENABLED is True
        assert settings.RATE_LIMIT_DEFAULT == "100/minute"
        assert settings.RATE_LIMIT_PIPELINE == "10/minute"
        assert settings.RATE_LIMIT_AGENTS == "30/minute"
        assert settings.RATE_LIMIT_WS == "60/minute"
        assert settings.RATE_LIMIT_HEALTH == "200/minute"

    def test_api_key_settings_loaded(self):
        """Test API key settings are loaded (may be from env)."""
        from config import settings
        assert settings.API_KEY_ENABLED is True
        assert isinstance(settings.API_KEYS, list)

    def test_api_keys_parsing_string(self):
        """Test API keys parsing from comma-separated string."""
        from config import Settings
        
        with patch.object(Settings, 'Config'):
            original_env_file = Settings.Config.env_file
            Settings.Config.env_file = ".env"
            
            settings = Settings(API_KEYS="key1,key2,key3")
            assert settings.API_KEYS == ["key1", "key2", "key3"]
            
            Settings.Config.env_file = original_env_file

    def test_api_keys_parsing_json(self):
        """Test API keys parsing from JSON string."""
        from config import Settings
        
        original_env_file = Settings.Config.env_file
        Settings.Config.env_file = ".env"
        
        settings = Settings(API_KEYS='["key1", "key2"]')
        assert settings.API_KEYS == ["key1", "key2"]
        
        Settings.Config.env_file = original_env_file


class TestLoggingSettings:
    """Tests for logging configuration."""

    def test_logging_settings_loaded(self):
        """Test logging settings are loaded (may be from env)."""
        from config import settings
        assert settings.LOG_LEVEL is not None
        assert settings.LOG_FORMAT is not None


class TestWebSocketSettings:
    """Tests for WebSocket configuration."""

    def test_websocket_defaults(self):
        """Test default WebSocket settings."""
        from config import settings
        
        assert settings.WS_HEARTBEAT_INTERVAL == 30
        assert settings.WS_MESSAGE_MAX_SIZE == 10 * 1024 * 1024


class TestDatabaseSettings:
    """Tests for database configuration."""

    def test_supabase_settings_loaded(self):
        """Test Supabase settings can be loaded."""
        from config import settings
        assert hasattr(settings, 'SUPABASE_URL')
        assert hasattr(settings, 'SUPABASE_KEY')


class TestBackwardCompatibility:
    """Tests for backward compatibility."""

    def test_old_config_import(self):
        """Test that old config.py import still works."""
        import config
        
        assert hasattr(config, 'settings')
        assert hasattr(config, 'AI_MODELS')
        assert hasattr(config, 'AGENT_CONFIGS')
        assert hasattr(config, 'PIPELINE_STAGES')

    def test_settings_instance(self):
        """Test settings is a Settings instance."""
        from config import settings, Settings
        assert isinstance(settings, Settings)


class TestModularImports:
    """Tests for direct modular imports."""

    def test_import_from_ai(self):
        """Test importing from ai module."""
        from config.ai import AI_MODELS
        assert "claude" in AI_MODELS

    def test_import_from_agents(self):
        """Test importing from agents module."""
        from config.agents import AGENT_CONFIGS
        assert "planner" in AGENT_CONFIGS

    def test_import_from_pipeline(self):
        """Test importing from pipeline module."""
        from config.pipeline import PIPELINE_STAGES
        assert "planning" in PIPELINE_STAGES

    def test_import_from_security(self):
        """Test importing from security module."""
        from config.security import RateLimitSettings
        assert hasattr(RateLimitSettings, 'model_fields')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
