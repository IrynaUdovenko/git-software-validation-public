class GitCommandExecutionError(Exception):
    """Raised when git command execution fails due to environment or system error."""
    pass

class InvalidGitCommandError(Exception):
    """Raised when an invalid Git command is detected (e.g. typo in command)."""
    pass

class GitCommandFailedError(Exception):
    """Raised when a valid Git command returns a non-zero exit code."""
    pass