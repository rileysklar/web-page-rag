"""
Pytest fixtures for testing.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def api_key_headers():
    """Create headers with API key."""
    return {settings.API_KEY_NAME: settings.API_KEY}

@pytest.fixture
def sample_url():
    """Sample URL for testing."""
    return "https://example.com"

@pytest.fixture
def sample_namespace():
    """Sample namespace for testing."""
    return "test_namespace"

@pytest.fixture
def sample_question():
    """Sample question for testing."""
    return "What is this website about?" 