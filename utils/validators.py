from pathlib import Path

from logging_config import loggers

git_logger = loggers["git_test"]


def assert_git_command_success(result, command: str):
    """
    Validates that a git command executed successfully (exit code 0).
    Logs stdout/stderr if it fails.
    """
    if result.returncode != 0:
        git_logger.error(f"Command failed: {command}")
        git_logger.error(f"STDOUT: {result.stdout.strip()}")
        git_logger.error(f"STDERR: {result.stderr.strip()}")
    assert result.returncode == 0, f"Git command failed: {command}"


def assert_git_command_failure(result, command: str):
    """
    Validates that a git command failed (non-zero exit code).
    Logs stdout/stderr if it unexpectedly succeeded.
    """
    if result.returncode == 0:
        git_logger.error(f"Unexpected success: {command}")
        git_logger.error(f"STDOUT: {result.stdout.strip()}")
    assert result.returncode != 0, f"Git command unexpectedly succeeded: {command}"


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
