from pathlib import Path

import pytest

from logging_config import loggers
from utils.helpers import create_temp_files_in_repo, run_git_command
from utils.validators import (
    validate_git_command_expected_failure,
    validate_git_command_success,
    assert_git_dir_structure_valid,
    assert_with_log,
)
from utils.exceptions import GitCommandFailedError

# Get the logger for git_test
git_logger = loggers["git_test"]


def stage_and_validate_files(repo_path: Path, target: list[str]) -> list[str]:
    """
    Stage files using 'git add <target>' and verify they were staged.

    Uses 'git ls-files' to confirm that expected files were successfully
    added to the Git index, since 'ls-files' lists all tracked (staged) files.
    """
    result = run_git_command(["git", "add"] + target, cwd=repo_path)
    validate_git_command_success(result, f"git add {target}")
    git_logger.info(f"Ran 'git add {' '.join(target)}' inside {repo_path}")

    result = run_git_command(["git", "ls-files"], cwd=repo_path)
    validate_git_command_success(result, "git ls-files")
    staged_files = result.stdout.strip().splitlines()
    git_logger.info(f"Staged files: {staged_files}")

    return staged_files

# =============== INIT TESTS ====================

@pytest.mark.phase1
@pytest.mark.core
def test_git_init_creates_git_folder(git_init_repo):
    """
    Verify that 'git init' creates a valid .git directory.

    Uses 'git_init_repo' fixture to initialize a Git repo
    in a temporary directory, then verifies that '.git' exists and is a directory.
    """
    git_dir = git_init_repo / ".git"
    git_logger.info(f"Checking if .git directory exists under initialized repo: {git_init_repo}")

    assert_with_log(git_dir.exists(), ".git directory was not created", git_logger)
    git_logger.info("'.git' directory exists.")

    assert_with_log(git_dir.is_dir(), ".git exists but is not a directory", git_logger)
    git_logger.info("'.git' is confirmed to be a directory.")


@pytest.mark.phase1
@pytest.mark.core
def test_git_init_structure_validity(git_init_repo):
    """
    Verify that 'git init' creates the expected internal .git structure.

    Uses the shared validator function to check presence and types
    of key .git directory components.
    """
    git_dir = git_init_repo / ".git"
    git_logger.info(f"Validating structure of .git directory: {git_dir}")

    assert_git_dir_structure_valid(git_dir)
    git_logger.info(f".git directory structure is valid for repo: {git_dir}")


# =============== ADD TESTS ====================

@pytest.mark.phase1
@pytest.mark.core
def test_git_add_single_file(git_init_repo):
    """
    Verify that 'git add <filename>' stages a single new file correctly.

    Uses 'git ls-files' to check that the file is tracked after staging.
    """
    created_files = create_temp_files_in_repo(git_init_repo, ["file1.txt"])
    staged_files = stage_and_validate_files(git_init_repo, [created_files[0].name])

    assert created_files[0].name in staged_files, f"{created_files[0].name} not found in staged files"
    git_logger.info(f"Confirmed that file '{created_files[0].name}' was staged successfully.")


@pytest.mark.phase1
@pytest.mark.core
def test_git_add_all_files(git_init_repo):
    """
    Verify that 'git add .' stages all new files in the working directory.

    Uses 'git ls-files' to confirm all created files are staged.
    """
    filenames = ["file2.txt", "file3.txt"]
    create_temp_files_in_repo(git_init_repo, filenames)
    staged_files = stage_and_validate_files(git_init_repo, ["."])

    for name in filenames:
        assert name in staged_files, f"{name} not found in staged files"
        git_logger.info(f"Confirmed that file '{name}' was staged successfully.")


# =============== COMMIT TESTS ====================


@pytest.mark.phase1
@pytest.mark.core
def test_git_commit_creates_commit_object(repo_with_staged_file):
    """
    Verify that 'git commit' creates a valid commit object.

    First checks that 'git rev-parse HEAD' fails before the commit,
    then runs 'git commit' and verifies that a valid commit hash is created.
    """
    repo_path, _ = repo_with_staged_file

    # Before commit, HEAD should not exist
    result = run_git_command(["git", "rev-parse", "HEAD"], cwd=repo_path)
    with pytest.raises(GitCommandFailedError):
        validate_git_command_expected_failure(result, "git rev-parse HEAD")

    git_logger.info("Confirmed that no commit existed before running 'git commit'")

    # Perform commit
    git_logger.info("Ran 'git commit'")
    result = run_git_command(["git", "commit", "-m", "Initial commit"], cwd=repo_path)
    validate_git_command_success(result, "git commit -m 'Initial commit'")

    # After commit, HEAD should point to a valid commit hash
    result = run_git_command(["git", "rev-parse", "HEAD"], cwd=repo_path)
    validate_git_command_success(result, "git rev-parse HEAD")
    commit_hash = result.stdout.strip()
    git_logger.info(f"Commit hash: {commit_hash}")

    assert len(commit_hash) == 40, "Invalid commit hash length"
    git_logger.info("Confirmed that commit object was created successfully.")


@pytest.mark.phase1
@pytest.mark.core
def test_git_log_shows_latest_commit(local_repo_with_commit):
    """
    Verify that 'git log' returns the latest commit with correct author and message.

    Uses a pre-configured repo with one commit. Checks that git log includes the commit.
    """
    repo_path = local_repo_with_commit
    result = run_git_command(["git", "log", "-1"], cwd=repo_path)

    validate_git_command_success(result, "git log -1")

    log_output = result.stdout
    git_logger.debug(f"Git log output:\n{log_output}")

    expected_author = "Local User <local@example.com>"
    expected_message = "Test commit"

    assert_with_log(
        expected_author in log_output,
        f"Expected author '{expected_author}' not found in git log output",
        logger=git_logger,
    )

    assert_with_log(
        expected_message in log_output,
        f"Expected commit message '{expected_message}' not found in git log output",
        logger=git_logger,
    )

    git_logger.info("Verified that 'git log' shows the latest commit with correct info.")


# =============== SMOKE FLOW ====================


@pytest.mark.phase1
@pytest.mark.core
@pytest.mark.integration
@pytest.mark.smoke
def test_git_minimal_working_to_committed_flow(git_init_repo, set_git_user_config):
    """
    Verify the flow from working directory -> staging -> committed.
    Ensures all core Git operations work together.
    """

    # Set config (local by default)
    set_git_user_config(git_init_repo)
    git_logger.info("Set local user.name and user.email.")

    # Create file
    file_path = create_temp_files_in_repo(git_init_repo, ["file.txt"])[0]
    assert_with_log(file_path.exists(), "file.txt not found in working directory", git_logger)
    git_logger.info("Created file.txt in working directory.")

    # Add to staging
    result = run_git_command(["git", "add", file_path.name], cwd=git_init_repo)
    validate_git_command_success(result, f"git add {file_path.name}")
    git_logger.info("Added file.txt to staging area.")

    # Commit
    result = run_git_command(["git", "commit", "-m", "Initial commit"], cwd=git_init_repo)
    validate_git_command_success(result, "git commit")
    git_logger.info("Committed file.txt with message 'Initial commit'.")

    # Verify in log
    result = run_git_command(["git", "log", "-1", "--name-only"], cwd=git_init_repo)
    validate_git_command_success(result, "git log -1 --name-only")

    log_output = result.stdout
    assert_with_log(
        "file.txt" in log_output,
        f"file.txt not found in latest commit log:\n{log_output}",
        git_logger,
    )
    git_logger.info("Verified file.txt appears in latest git log.")
