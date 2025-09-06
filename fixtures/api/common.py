import os
import pytest

@pytest.fixture(scope="session")
def base_url():
    """Read base URL from environment variable or fallback to localhost."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")