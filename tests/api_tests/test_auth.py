import requests
import pytest
from utils.api_validators import assert_json_response, assert_user_response, assert_token_response, assert_token_payload
from utils.constants import API_TIMEOUT, API_MAX_RESPONSE_TIME
from logging_config import loggers

# Get the logger for api tests
api_logger = loggers["api_test"]

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.POC
def test_register_user(base_url, user_payload):
    """Positive test: register a new user and validate response."""
    response = requests.post(f"{base_url}/users", json=user_payload, timeout=API_TIMEOUT)
    elapsed = round(response.elapsed.total_seconds(), 3)
    api_logger.info(f'POST /users returned: {response.status_code} in : {elapsed} seconds.')
    api_logger.debug(f" Response body : {response.text}")
    # Common checks + JSON validation
    parsed_data = assert_json_response(response, expected_status=201)

    # Body validation
    assert_user_response(parsed_data, expected_name=user_payload["name"], expected_email=user_payload["email"])
    api_logger.info("User response status code and body validated successfully.")
    # Performance check
    assert elapsed < API_MAX_RESPONSE_TIME, "Response took too long"

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.POC
def test_login_user(base_url, register_user):
    """Positive test: register a new user and login to get token."""
    user_data, password = register_user
    login_payload = {"email": user_data["email"], "password": password}
    response = requests.post(base_url+"/users/login", json=login_payload, timeout=API_TIMEOUT)
    elapsed = round(response.elapsed.total_seconds(), 3)
    api_logger.info(f'POST /users/login returned: {response.status_code} in : {elapsed} seconds.')
    # Common checks + JSON validation
    parsed_data = assert_json_response(response, expected_status=200)

    # Body validation
    assert_token_response(parsed_data)
    assert_token_payload(parsed_data["access_token"], expected_email=login_payload["email"])
    api_logger.info("Token response status code and body validated successfully.")

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.POC
def test_get_me(base_url, login_user):
    """Positive test: fetch current user data with valid token."""
    headers = {"Authorization": f"Bearer {login_user['token']}"}
    response = requests.get(f"{base_url}/users/me", headers=headers, timeout=API_TIMEOUT)

    elapsed = round(response.elapsed.total_seconds(), 3)
    api_logger.info(f"GET /users/me returned: {response.status_code} in {elapsed} seconds.")
    
    parsed = assert_json_response(response, expected_status=200)
    assert_user_response(parsed, expected_name=login_user["name"], expected_email=login_user["email"], expected_last_login=login_user["login_time"])
    api_logger.info("User /me response validated successfully.")
