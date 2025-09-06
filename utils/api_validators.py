from logging_config import loggers

# Get the logger for api tests
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
    expected_last_login=None,
):
    """Validate user response JSON structure and values."""

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
        else:
            assert data[field] == expected, f"Expected {field}={expected}, got {data[field]}"
            infra_logger.debug(f"Field '{field}' has expected value: {expected}")

    # Forbidden fields
    forbidden_fields = ["password", "hashed_password"]
    for field in forbidden_fields:
        assert field not in data, f"Response should not expose '{field}'"
        infra_logger.debug(f"Field '{field}' is correctly not present in response.")
