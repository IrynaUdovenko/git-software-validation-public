from pathlib import Path
from utils.exceptions import InvalidGitCommandError, GitCommandFailedError
from logging_config import loggers

git_logger = loggers["git_test"]


def validate_git_command_success(result, command: str, expected_failure: bool = False):
    """
    Validates the outcome of a Git command.
    
    - Raises InvalidGitCommandError if the command is not recognized by Git.
    - Raises GitCommandFailedError for all other non-zero return codes.
    """
    if result.returncode != 0:
        # Log ERROR only if it's an unexpected failure
        log_fn = git_logger.info if expected_failure else git_logger.error
        log_fn(f"Git command failed: {command}")
        log_fn(f"STDOUT: {result.stdout.strip()}")
        log_fn(f"STDERR: {result.stderr.strip()}")
        
        # Detect invalid command from stderr
        if "git: '" in result.stderr and "' is not a git command" in result.stderr:
            raise InvalidGitCommandError(f"Invalid Git command: {command}")
        
        raise GitCommandFailedError(f"Git command failed: {command}")
    
    git_logger.debug(f"Git command succeeded: {command}")

def validate_git_command_expected_failure(result, context: str):
    return validate_git_command_success(result, context, expected_failure=True)


def assert_with_log(condition: bool, message: str, logger=None):
    """
    Assert wrapper that logs the failure message only if assertion fails.
    """
    try:
        assert condition, message
    except AssertionError:
        if logger:
            logger.error(f"Assertion failed: {message}")
        else:
            print(f"Assertion failed: {message}")
        raise


def assert_git_dir_structure_valid(git_dir: Path):
    """
    Validates the minimal required structure of a .git directory.

    Designed to work for both freshly initialized and cloned repositories.
    Only strictly required components are checked.
    """
    required_entries = {
        "HEAD": "file",
        "config": "file",
        "hooks": "dir",
        "info": "dir",
        "objects": "dir",
        "refs": "dir",
    }

    for entry, expected_type in required_entries.items():
        path = git_dir / entry
        assert path.exists(), f"Missing required {expected_type}: {entry}"
        if expected_type == "file":
            assert path.is_file(), f"{entry} exists but is not a file"
        elif expected_type == "dir":
            assert path.is_dir(), f"{entry} exists but is not a directory"

    # Validate that HEAD points to a local branch or ref
    head_file = git_dir / "HEAD"
    if head_file.exists():
        head_content = head_file.read_text().strip()
        assert head_content.startswith("ref: refs/heads/") or "HEAD" in head_content.lower(), f"Unexpected HEAD content: {head_content}"
