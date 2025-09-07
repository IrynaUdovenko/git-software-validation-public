import pytest
import uuid
from logging_config import loggers
import requests
from utils.constants import API_TIMEOUT
from utils.api_validators import assert_json_response
from datetime import datetime, timezone

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
def register_user_factory():
    """Factory fixture to register users before test and return its data."""
    def _make_register_user(base_url, user_payload):
        infra_logger.info(f'Registering user with email : {user_payload["email"]}')
        response = requests.post(base_url+"/users", json=user_payload, timeout=API_TIMEOUT)
        elapsed = round(response.elapsed.total_seconds(), 3)
        infra_logger.info(f'POST /users returned: {response.status_code} in : {elapsed} seconds.')
        data = assert_json_response(response, expected_status=201)
        infra_logger.info("User successfully registered.")
        return data, user_payload["password"]
    return _make_register_user

@pytest.fixture
def register_user(register_user_factory, base_url, user_payload):
    """Simple fixture to register one user without custom params."""
    return register_user_factory(base_url, user_payload)

@pytest.fixture
def login_user(base_url, register_user):
    """Register and login user, return access token."""
    user_data, password = register_user
    login_payload = {"email": user_data["email"], "password": password}
    infra_logger.info(f'Log in user with email : {login_payload["email"]}')
    before_login_time = datetime.now(timezone.utc)
    response = requests.post(f"{base_url}/users/login", json=login_payload, timeout=API_TIMEOUT)
    parsed = assert_json_response(response, expected_status=200)
    infra_logger.info("User successfully logged in and token received.")
    return {
        "id": user_data["id"],
        "name": user_data["name"],
        "email": user_data["email"],
        "password": password,
        "token": parsed["access_token"],
        "login_time": before_login_time
    }
