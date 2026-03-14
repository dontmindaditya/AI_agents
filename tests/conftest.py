"""Pytest configuration for AgentHub tests."""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import os
from unittest.mock import MagicMock, patch

# Set test environment variables
os.environ.setdefault("APP_NAME", "AgentHub Test")
os.environ.setdefault("LOG_LEVEL", "ERROR")
os.environ.setdefault("LOG_FORMAT", "text")
os.environ.setdefault("API_KEY_ENABLED", "true")
os.environ.setdefault("API_KEYS", "test-key-1,test-key-2")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names."""
    for item in items:
        if "test_agent_system" in item.nodeid or "test_pipeline" in item.nodeid:
            item.add_marker("integration")
        else:
            item.add_marker("unit")
