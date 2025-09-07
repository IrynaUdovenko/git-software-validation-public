import pytest
import uuid
from logging_config import loggers
import requests
from utils.constants import API_TIMEOUT
from utils.api_validators import assert_json_response

infra_logger = loggers["infra"]

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

@pytest.fixture
def register_user(base_url, user_payload):    
    """Fixture to register a user before test and return its data."""
    infra_logger.info(f'Registering user with email : {user_payload["email"]}')
    response = requests.post(base_url+"/users", json=user_payload, timeout=API_TIMEOUT)
    elapsed = round(response.elapsed.total_seconds(), 3)
    infra_logger.info(f'POST /users returned: {response.status_code} in : {elapsed} seconds.')
    data = assert_json_response(response, expected_status=201)
    infra_logger.info("User successfully registered.")
    return data, user_payload["password"]