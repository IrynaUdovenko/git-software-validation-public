# === Base for API errors ===
class AppError(Exception):
    """Base class for all custom application errors (used in API)."""
    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str | None = None):
        if message is not None:
            self.message = message

# === API-related exceptions ===
class EmailAlreadyExists(AppError):
    """Raised when a user with the same email already exists."""
    status_code = 409
    message = "User with this email already exists."
    pass

class DatabaseError(AppError):
    """Generic error for any unexpected DB-related issue."""
    status_code = 500
    message = "Unexpected database error."

class DatabaseUnavailable(AppError):  
    """Raised when the database is unreachable or unavailable."""
    status_code = 503
    message = "Database is unavailable."

class InvalidTokenError(AppError):
    """Raised when a JWT token is invalid or expired."""
    status_code = 401
    message = "Invalid or expired token"


# === Git CLI test exceptions (not for API) ===
class GitCommandExecutionError(Exception):
    """Raised when git command execution fails due to environment or system error."""
    pass

class InvalidGitCommandError(Exception):
    """Raised when an invalid Git command is detected (e.g. typo in command)."""
    pass

class GitCommandFailedError(Exception):
    """Raised when a valid Git command returns a non-zero exit code."""
    pass
