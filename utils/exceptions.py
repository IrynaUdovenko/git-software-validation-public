class GitCommandExecutionError(Exception):
    """Raised when git command execution fails due to environment or system error."""
    pass

class InvalidGitCommandError(Exception):
    """Raised when an invalid Git command is detected (e.g. typo in command)."""
    pass

class GitCommandFailedError(Exception):
    """Raised when a valid Git command returns a non-zero exit code."""
    pass

class EmailAlreadyExists(Exception):
    """Raised when a user with the same email already exists."""
    pass

class DatabaseError(Exception):
    """Generic error for any unexpected DB-related issue."""
    pass