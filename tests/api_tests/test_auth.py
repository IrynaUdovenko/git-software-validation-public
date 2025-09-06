import requests
import pytest
from utils.api_validators import assert_json_response, assert_user_response
from utils.constants import API_TIMEOUT
from logging_config import loggers

# Get the logger for api tests
api_logger = loggers["api_test"]

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.POC
def test_register_user(base_url, user_payload):
    """Positive test: register a new user and validate response."""
    response = requests.post(f"{base_url}/users", json=user_payload, timeout=API_TIMEOUT)
    api_logger.info(f'Sending POST request to url: {base_url}/users with payload : user name : {user_payload["name"]}, user email : {user_payload["email"]}')
    api_logger.info(f'Response received with status code: {response.status_code} and body : {response.text}')
    # Common checks + JSON validation
    parsed_data = assert_json_response(response, expected_status=201)

    # Body validation
    assert_user_response(parsed_data, expected_name=user_payload["name"], expected_email=user_payload["email"])
    api_logger.info("User response status code and body validated successfully.")
    # Performance check
    assert response.elapsed.total_seconds() < 1, "Response took too long"