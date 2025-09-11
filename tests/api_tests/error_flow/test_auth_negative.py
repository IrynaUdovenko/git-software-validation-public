import requests
from utils.constants import API_TIMEOUT
from logging_config import loggers
from utils.api_validators import assert_json_response, assert_simple_error_response, assert_complex_error_response
import pytest

# Get the logger for api tests
api_logger = loggers["api_test"]

def post_and_validate(url: str, payload: dict, expected_status: int):
    """
    Send a POST request with given payload, validate status and JSON format.
    Returns parsed JSON data for further validation in tests.
    """
    api_logger.info(f"Attempting POST {url} with payload: {payload}")
    response = requests.post(url, json=payload, timeout=API_TIMEOUT)
    elapsed = round(response.elapsed.total_seconds(), 3)
    api_logger.info(f"POST {url} returned: {response.status_code} in {elapsed} seconds.")
    api_logger.debug(f"Response body: {response.text}")

    parsed_data = assert_json_response(response, expected_status=expected_status)
    return parsed_data

# Negative test cases for user registration

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.error_flow
def test_register_duplicate_email(base_url, register_user):
    """Negative test: attempt to register a user with an email that already exists."""
    user_data, _ = register_user
    api_logger.info(f"Succesfully registered user with email: {user_data['email']}")
    duplicate_payload = {
        "name": "Another User",
        "email": user_data["email"],  # Same email as the registered user
        "password": "newpassword123"
    }
    parsed_data = post_and_validate(f"{base_url}/users", payload=duplicate_payload, expected_status=409)
    # Check for error message in response
    assert_simple_error_response(parsed_data, expected_message="Email already exists")
    api_logger.info("Duplicate email registration correctly failed with appropriate error message.")

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.error_flow
def test_register_incorrect_format_email(base_url, user_payload):
    """Negative test: attempt to register a user with an email with incorrect format."""
    bad_payload = user_payload.copy()
    bad_payload["email"] = bad_payload["email"].replace("@", "")
    parsed_data = post_and_validate(f"{base_url}/users", payload=bad_payload, expected_status=422)

    # Check for error message in response
    assert_complex_error_response(parsed_data, expected_errors=[{"loc": ["body", "email"], "msg": "valid email"}])
    api_logger.info("Wrong format email registration correctly failed with appropriate error message.")

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.error_flow
def test_register_too_short_password(base_url, user_payload):
    """Negative test: attempt to register a user with a short password."""
    bad_payload = user_payload.copy()
    bad_payload["password"] = bad_payload["password"][:3]  # Make password too short
    parsed_data = post_and_validate(f"{base_url}/users", payload=bad_payload, expected_status=422)

    # Check for error message in response
    assert_complex_error_response(parsed_data, expected_errors=[{"loc": ["body", "password"], "msg": "8 characters"}])
    api_logger.info("Too short password registration correctly failed with appropriate error message.")

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.error_flow
def test_register_long_name_and_missing_password(base_url, user_payload):
    """Negative test: attempt to register a user with too long name and without password."""
    bad_payload = user_payload.copy()
    bad_payload["name"] = "A" * 60   # Make name too long (over 50 chars)
    bad_payload.pop("password")      # Remove password field

    parsed_data = post_and_validate(f"{base_url}/users", payload=bad_payload, expected_status=422)

    assert_complex_error_response(
        parsed_data,
        expected_errors=[
            {"loc": ["body", "name"], "msg": "50 characters"},
            {"loc": ["body", "password"], "msg": "field required"},
        ]
    )
    api_logger.info("Registration with too long name and missing password correctly failed with 2 validation errors.")

# Negative test cases for user login

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.error_flow
def test_login_wrong_password(base_url, register_user):
    """Negative test: attempt to login with correct email but wrong password."""
    user_data, password = register_user
    api_logger.info(f"Succesfully registered user with email: {user_data['email']} and password.")
    bad_payload = {"email": user_data["email"], "password": password + "wrong"}
    parsed = post_and_validate(f"{base_url}/users/login", payload=bad_payload, expected_status=401)
    assert_simple_error_response(parsed, "invalid email or password")
    api_logger.info("Login with wrong password correctly failed with 401.")

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.error_flow
def test_login_unknown_email(base_url, register_user):
    """Negative test: attempt to login with non-existing email."""
    user_data, password = register_user
    api_logger.info(f"Succesfully registered user with email: {user_data['email']} and password.")
    bad_payload = {"email": user_data["email"].replace("com","ua"), "password": password}
    parsed = post_and_validate(f"{base_url}/users/login", payload=bad_payload, expected_status=401)
    assert_simple_error_response(parsed, "invalid email or password")
    api_logger.info("Login with unknown email correctly failed with 401.")

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.error_flow
def test_login_missing_password(base_url, register_user):
    """Negative test: attempt to login without password field."""
    user_data, _ = register_user
    api_logger.info(f"Succesfully registered user with email: {user_data['email']} and password.")
    bad_payload = {"email": user_data["email"]}
    parsed = post_and_validate(f"{base_url}/users/login", payload=bad_payload, expected_status=422)
    assert_complex_error_response(parsed, [{"loc": ["body", "password"], "msg": "field required"}])
    api_logger.info("Login without password correctly failed with 422.")

# Negative test cases for /users/me endpoint

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.error_flow
def test_get_me_without_token(base_url):
    """Negative test: attempt to fetch /me without Authorization header."""
    response = requests.get(f"{base_url}/users/me", timeout=API_TIMEOUT)
    parsed = assert_json_response(response, expected_status=401)
    assert_simple_error_response(parsed, "not authenticated")
    api_logger.info("/me without token correctly failed with 401.")

@pytest.mark.phase2
@pytest.mark.users
@pytest.mark.error_flow
@pytest.mark.parametrize("scenario, expected_msg", [
    ("wrong_scheme", "not authenticated"),
    ("invalid_format", "not enough segments"),
    ("tampered_token", "signature verification failed"),
])
def test_me_invalid_token_scenarios(base_url, login_user, scenario, expected_msg):
    """Negative tests: /me with wrong scheme, badly formatted token, or tampered signature."""

    token_parts = login_user["token"].split(".")

    match scenario:
        case "wrong_scheme":
            headers = {"Authorization": f"Token {login_user['token']}"}

        case "invalid_format":
            headers = {"Authorization": f"Bearer {'.'.join(token_parts[:2])}"}

        case "tampered_token":
            headers = {"Authorization": f"Bearer {'.'.join(token_parts[:2])}.{token_parts[2][:-1]}x"}

        case _:
            pytest.skip(f"Unknown scenario: {scenario}")

    api_logger.info(f"Sending /me request with {scenario} headers: {headers}")
    response = requests.get(f"{base_url}/users/me", headers=headers, timeout=API_TIMEOUT)
    parsed = assert_json_response(response, expected_status=401)
    assert_simple_error_response(parsed, expected_msg)
    api_logger.info(f"/me with scenario={scenario} correctly failed with 401.")