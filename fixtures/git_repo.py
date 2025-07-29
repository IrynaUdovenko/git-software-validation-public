from pathlib import Path
from typing import Callable

import pytest

from logging_config import loggers
from utils.helpers import create_temp_files_in_repo, run_git_command
from utils.validators import validate_git_command_success

# Get the loggers for different parts of the project
infra_logger = loggers["infra"]


@pytest.fixture
def git_init_repo(tmp_path, request) -> Path:
    """
    Creates a temporary directory and initializes a new Git repository in it,
    with default branch set to 'main'.

    - Sets global default branch to 'main' (this command is already verified in Phase1)
    - Use pytest's built-in tmp_path fixture to create a temporary, isolated directory.
    - Initializes a Git repo in that directory
    - Cleans up the global setting after test
    """
    # Set global default branch to 'main'
    result = run_git_command(["git", "config", "--global", "init.defaultBranch", "main"], cwd=tmp_path)
    validate_git_command_success(result, "git config --global init.defaultBranch main")

    # Register cleanup to unset the global config after test
    def unset_default_branch():
        run_git_command(["git", "config", "--global", "--unset", "init.defaultBranch"], cwd=tmp_path)

    request.addfinalizer(unset_default_branch)

    # Initialize the Git repo
    result = run_git_command(["git", "init"], cwd=tmp_path)
    validate_git_command_success(result, "git init")

    return tmp_path


@pytest.fixture
def repo_with_staged_file(git_init_repo, set_git_user_config) -> tuple[Path, Path]:
    """
    Fixture that provides a Git repository with one staged file and minimal required config.

    Uses 'git init' and 'git add' internally (already tested),
    and sets global config for user.name and user.email to allow git commit to succeed.

    Global config is cleaned up even if the test fails (via set_git_user_config logic).
    """
    # Apply global config via fixture-factory
    set_git_user_config(git_init_repo, global_=True)

    # Create and stage file
    test_file = create_temp_files_in_repo(git_init_repo, ["file.txt"])[0]
    result = run_git_command(["git", "add", test_file.name], cwd=git_init_repo)
    validate_git_command_success(result, f"git add {test_file.name}")

    infra_logger.debug(f"Staged file: '{test_file.name}' in repo: {git_init_repo}")

    return git_init_repo, test_file


@pytest.fixture
def commit_temp_file_with_local_config(set_git_user_config) -> Callable[[Path], Path]:
    """
    Factory Fixture that applies local Git user config, stages a file, and commits it.
    Designed to be reused after 'git init' or 'git clone'.

    Steps:
    - Sets user.name and user.email locally.
    - Creates a file 'test.txt' in the repo.
    - Stages and commits the file.
    """

    def _apply(repo_path: Path) -> Path:
        # Apply local config
        set_git_user_config(repo_path, username="Local User", email="local@example.com")

        # Create and stage file
        file_path = create_temp_files_in_repo(repo_path, ["test.txt"])[0]
        result = run_git_command(["git", "add", file_path.name], cwd=repo_path)
        validate_git_command_success(result, f"git add {file_path.name}")

        # Commit
        result = run_git_command(["git", "commit", "-m", "Test commit"], cwd=repo_path)
        validate_git_command_success(result, "git commit")

        infra_logger.info("Created repo with local config and initial commit.")

        return repo_path

    return _apply


@pytest.fixture
def local_repo_with_commit(git_init_repo, commit_temp_file_with_local_config) -> Callable[[Path], Path]:
    """
    Fixture that initializes a Git repository (using git_init_repo),
    sets local user.name and user.email (via set_git_user_config),
    stages a file, and performs a commit.

    Useful for tests that need a ready-to-use repo with local config and initial commit.

    This fixture is validated via `test_git_minimal_working_to_committed_flow`.
    Safe to reuse in integration and system-level tests.
    """
    repo_path = git_init_repo

    # Apply local config via fixture-factory
    return commit_temp_file_with_local_config(repo_path)


@pytest.fixture
def set_git_user_config(request) -> Callable[[Path, str, str, bool], None]:
    """
    Fixture-factory for configuring Git user.name and user.email.

    This is NOT a regular fixture — it returns a callable (_apply) that
    must be invoked manually inside the test.

    Supports both local (default) and global (--global) config.
    If global config is set, it will automatically be cleaned up after the test.

    Example usage:
        set_git_user_config(repo_path)                            # Local config
        set_git_user_config(repo_path, global_=True)              # Global config with cleanup
        set_git_user_config(repo_path, username="Alice", email="alice@example.com" )     # Custom name and email
    """

    def _apply(repo_path, username="Test User", email="test@example.com", global_=False):
        scope_args = ["--global"] if global_ else []

        # Set user.name
        result = run_git_command(["git", "config"] + scope_args + ["user.name", username], cwd=repo_path)
        validate_git_command_success(result, f"git config {scope_args} user.name {username}")

        # Set user.email
        result = run_git_command(["git", "config"] + scope_args + ["user.email", email], cwd=repo_path)
        validate_git_command_success(result, f"git config {scope_args} user.email {email}")

        # Automatically clean up global config after the test
        if global_:

            def cleanup():
                infra_logger.debug("Cleaning up global Git config (user.name, user.email)")
                run_git_command(["git", "config", "--global", "--unset", "user.name"], cwd=repo_path)
                run_git_command(
                    ["git", "config", "--global", "--unset", "user.email"],
                    cwd=repo_path,
                )

            request.addfinalizer(cleanup)

    return _apply
