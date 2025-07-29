import pytest
from utils.exceptions import GitCommandExecutionError
from utils.helpers import run_git_command
from logging_config import loggers

# Get the logger for git_test
git_logger = loggers["git_test"]

@pytest.mark.infra
def test_git_command_invalid_path_raises_custom_exception(tmp_path):
    invalid_path = tmp_path / "nonexistent-dir"
    with pytest.raises(GitCommandExecutionError) as exc_info:
        run_git_command(["git", "status"], cwd=invalid_path)
    git_logger.info(f"{exc_info.value} raised for invalid path")
    assert "Git command failed in" in str(exc_info.value)
    assert "nonexistent-dir" in str(exc_info.value), "Expected path not found in exception message"
    assert isinstance(exc_info.value.__cause__, OSError), "Expected OSError as cause"
    git_logger.info("Successfully raised GitCommandExecutionError for invalid directory.")
    

