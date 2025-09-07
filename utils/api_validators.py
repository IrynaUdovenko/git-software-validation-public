from logging_config import loggers
from jose import jwt
from utils.constants import LAST_LOGIN_DELTA
from datetime import datetime, timedelta, timezone
from typing import Any

infra_logger = loggers["infra"]

def assert_json_response(response, expected_status: int) -> dict:
    """Validate status, Content-Type and JSON validity."""

    infra_logger.debug("Starting validation of API call response...")

    # Status code
    assert response.status_code == expected_status, (
        f"Expected {expected_status} status code, got {response.status_code}. Body: {response.text}"
    )

    infra_logger.debug(f"Expected status {expected_status} received.")

    # Content-Type
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, f"Unexpected Content-Type: {content_type}"
    infra_logger.debug("Content-Type is application/json as expected.")

    # JSON validity
    try:
        data = response.json()
        infra_logger.debug(f"Response body is valid JSON with data : {data}")
    except ValueError:
        raise AssertionError("Response body is not a valid JSON")

    return data

def assert_user_response(
    data: dict,
    expected_name: str,
    expected_email: str,
    expected_last_login: datetime | None = None,
):
    """Validate user response JSON structure and values."""
    infra_logger.debug("Starting validation of response body structure...")

    # Expected values (None means "we still expect field but value check is None")
    expected_fields = {
        "id": None,  # special case, check type separately
        "name": expected_name,
        "email": expected_email,
        "last_login": expected_last_login,
    }

    for field, expected in expected_fields.items():
        assert field in data, f"Missing '{field}' in response"
        infra_logger.debug(f"Field '{field}' is present in response.")
        if field == "id":
            assert isinstance(data["id"], int), f"id should be int, got {type(data['id'])}"
            infra_logger.debug("Field 'id' is of type int as expected.")
        elif field == "last_login" and expected is not None:
            # Convert API value (ISO string) to datetime
            parsed = datetime.fromisoformat(data["last_login"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            assert expected <= parsed <= now + timedelta(seconds=LAST_LOGIN_DELTA), (
                f"last_login {parsed} not within expected range "
                f"[{expected}, {now + timedelta(seconds=LAST_LOGIN_DELTA)}]"
            )
            infra_logger.debug(f"Field 'last_login':{parsed}  is within expected range around login time: {expected}.")

        else:
            assert data[field] == expected, f"Expected {field}={expected}, got {data[field]}"
            infra_logger.debug(f"Field '{field}' has expected value: {expected}")

    # Forbidden fields
    forbidden_fields = ["password", "hashed_password"]
    for field in forbidden_fields:
        assert field not in data, f"Response should not expose '{field}'"
        infra_logger.debug(f"Field '{field}' is correctly not present in response.")

def assert_token_response(data: dict, expected_type="bearer"):
    """Validate structure of token response (without decoding JWT)."""
    infra_logger.debug("Starting validation of token response (without decoding JWT)...")
    required_fields = ["access_token", "token_type"]

    for field in required_fields:
        assert field in data, f"Missing '{field}' in token response"
        infra_logger.debug(f"Field '{field}' is present in response.")


    assert data["token_type"] == expected_type, f"Unexpected token_type: {data['token_type']}"
    infra_logger.debug(f"'Token type' has expected value: {expected_type}")
    assert isinstance(data["access_token"], str), "access_token should be a string"
    assert len(data["access_token"]) > 0, "access_token is empty"
    infra_logger.debug("Token exists and is a non-empty string.")

def assert_token_payload(token: str, expected_email: str):
    """Decode JWT without verifying signature and validate claims."""
    infra_logger.debug("Starting validation of JWT token payload...")

    parts = token.split(".")
    assert len(parts) == 3, f"Invalid JWT format: {token}"
    infra_logger.debug("Received token has valid JWT format (consists of three parts).")
    # Getting payload without signature verification
    claims = jwt.get_unverified_claims(token)

    # Claims validation
    assert claims.get("sub") == expected_email, f"Expected sub={expected_email}, got {claims.get('sub')}"
    infra_logger.debug(f"'sub' claim has expected email value: {expected_email}")
    assert "exp" in claims, "Missing 'exp' in token"
    assert claims["exp"] > 0, f"Invalid exp claim: {claims['exp']}"
    infra_logger.debug("'exp' claim is present and valid in token payload part.")

def assert_simple_error_response(data: dict, expected_message: str):
    """
    Validate simple error response (401, 403, 404, 409).
    Expects 'detail' to be a string containing expected_message.
    """
    infra_logger.debug(f"Validating simple error response: {data}")
    assert "detail" in data, "Missing 'detail' in error response"
    assert isinstance(data["detail"], str), f"Expected 'detail' to be str, got {type(data['detail'])}"

    detail = data["detail"].lower()
    expected = expected_message.lower()

    assert expected in detail, f"Expected '{expected_message}' in detail='{data['detail']}'"
    infra_logger.debug(f"Error detail contains expected message: {expected_message}")


def assert_complex_error_response(data: dict, expected_errors: list[dict[str, Any]]):
    """
    Validate unprocessable entity response (422).
    Expects 'detail' to be a list of dicts and all expected_errors
    to appear there with matching 'loc' and 'msg' substrings.
    
    Example expected_errors:
    [
        {"loc": ["body", "email"], "msg": "valid email address"},
        {"loc": ["body", "password"], "msg": "too short"},
    ]
    """
    infra_logger.debug(f"Validating unprocessable entity error response: {data}")
    assert "detail" in data, "Missing 'detail' in error response"
    assert isinstance(data["detail"], list), f"Expected list of validation errors, got {type(data['detail'])}"

    actual_errors = [err for err in data["detail"] if isinstance(err, dict)]

    for expected in expected_errors:
        exp_loc = expected.get("loc")
        exp_msg = expected.get("msg", "").lower()

        found = False
        for err in actual_errors:
            # Check location matches exactly
            if exp_loc and err.get("loc") != exp_loc:
                continue
            # Check message substring
            if exp_msg and exp_msg not in err.get("msg", "").lower():
                continue
            found = True
            break

        assert found, f"Expected error {expected} not found in {actual_errors}"
        infra_logger.debug(f"Validation error found for {expected}")