import pytest
import uuid

@pytest.fixture
def user_payload_factory():
    """Factory fixture to generate unique user payloads."""
    def _make_user_payload(name: str = "Test User", password: str = "password123"):
        # Use last 8 chars from UUID to reduce chance of collisions
        unique_email = f"test_{uuid.uuid4().hex[-8:]}@example.com"
        return {
            "name": name,
            "email": unique_email,
            "password": password,
        }
    return _make_user_payload


@pytest.fixture
def user_payload(user_payload_factory):
    """Simple fixture for one user payload without custom params."""
    return user_payload_factory()
