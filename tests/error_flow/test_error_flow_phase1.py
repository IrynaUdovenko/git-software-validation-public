import pytest
from logging_config import loggers
from utils.helpers import run_git_command, create_temp_files_in_repo
from utils.validators import validate_git_command_expected_failure, validate_git_command_success
from utils.exceptions import InvalidGitCommandError, GitCommandFailedError

# Get the logger for git_test
git_logger = loggers["git_test"]

@pytest.mark.phase1
@pytest.mark.remote
@pytest.mark.error_flow
def test_git_clone_non_existent_repo(tmp_path):
    """
    Attempt to clone a non-existent repo and expect failure.

    Uses a fake path as remote; validates that git clone fails as expected.
    """
    # Define a non-existent path
    fake_remote_path = tmp_path / "nonexistent-repo.git"
    clone_target_path = tmp_path / "client-clone"

    # Attempt to clone it
    result = run_git_command(
        ["git", "clone", str(fake_remote_path), str(clone_target_path)],
        cwd=tmp_path,
    )
    with pytest.raises(GitCommandFailedError):
        validate_git_command_expected_failure(result, "git clone from non-existent repo")

    # Validate stderr content contains known Git error
    assert any(
    phrase in result.stderr
    for phrase in [
        "does not appear to be a git repository",
        "could not read from remote repository",
        "repository" and "does not exist",
    ]
)
    git_logger.info("Correctly failed to clone non-existent repo with expected error message.")


@pytest.mark.phase1
@pytest.mark.core
@pytest.mark.error_flow
def test_git_add_non_existing_file(git_init_repo):
    """
    Verify that 'git add' fails when trying to stage a non-existing file.
    """
    non_existing_file = "fake.txt"
    result = run_git_command(["git", "add", non_existing_file], cwd=git_init_repo)
    with pytest.raises(GitCommandFailedError):
        validate_git_command_expected_failure(result, f"git add {non_existing_file}")
    
    assert "did not match any files" in result.stderr or "fatal" in result.stderr
    git_logger.info(f"Confirmed: 'git add' fails for non-existing file '{non_existing_file}'.")


@pytest.mark.phase1
@pytest.mark.core
@pytest.mark.error_flow
def test_commit_without_user_config(git_init_repo):
    """
    Verify that 'git commit' fails if user.name and user.email are not configured.
    """
    # Create and stage file
    test_file = create_temp_files_in_repo(git_init_repo, ["file.txt"])[0]
    run_git_command(["git", "add", test_file.name], cwd=git_init_repo)

    # Try to commit without config
    result = run_git_command(["git", "commit", "-m", "Test commit"], cwd=git_init_repo)
    with pytest.raises(GitCommandFailedError):
        validate_git_command_expected_failure(result, "git commit without config")

    assert "user.name" in result.stderr or "user.email" in result.stderr
    git_logger.info("Confirmed: 'git commit' fails if user.name and user.email are not set.")


@pytest.mark.phase1
@pytest.mark.remote
@pytest.mark.error_flow
def test_remote_add_with_invalid_url(local_repo_with_commit):
    """
    Verify that 'git remote add' with invalid URL does not fail immediately,
    but 'git push' will fail later.
    """
    invalid_remote_url = "ht!tp:/invalid-url"
    # Setup: create a local repo with a commit
    repo_path = local_repo_with_commit

    # Add remote with invalid URL
    result = run_git_command(["git", "remote", "add", "origin", str(invalid_remote_url)], cwd=repo_path)
    validate_git_command_success(result, f"git remote add with invalid url {invalid_remote_url} is accepted")

    # Push commit
    result = run_git_command(["git", "push", "-u", "origin", "main"], cwd=repo_path)
    with pytest.raises(GitCommandFailedError):
        validate_git_command_expected_failure(result, f"git push to {invalid_remote_url}")

    assert "fatal" in result.stderr or "unable to access" in result.stderr
    git_logger.info("Confirmed: 'git remote add' with invalid URL is not rejected, but 'git push' fails.")


@pytest.mark.phase1
@pytest.mark.remote
@pytest.mark.error_flow
def test_push_without_remote(local_repo_with_commit):
    """
    Verify that 'git push' fails if no remote is configured.
    """
    # Setup: create a local repo with a commit
    repo_path= local_repo_with_commit

    # Try to push without remote
    result = run_git_command(["git", "push", "-u", "origin", "main"], cwd=repo_path)
    with pytest.raises(GitCommandFailedError):
        validate_git_command_expected_failure(result, "git push without remote")

    assert "No configured push destination" in result.stderr or "fatal" in result.stderr    
    git_logger.info("Confirmed: 'git push' fails when no remote is configured.")


@pytest.mark.phase1
@pytest.mark.error_flow
def test_push_without_upstream_set(local_repo_with_commit, git_bare_server):
    """
    Verify that 'git push' fails if remote exists but upstream branch is not set.
    """
    # Setup: create a local repo with a commit and remote server
    repo_path = local_repo_with_commit
    remote_path = git_bare_server

    # Add remote (valid but unused path)
    result = run_git_command(["git", "remote", "add", "origin", str(remote_path)], cwd=repo_path)
    validate_git_command_success(result, f"git remote add origin {str(remote_path)}")
    git_logger.info("Added remote 'origin' to client repo.")

    # Try to push without tracking branch
    result = run_git_command(["git", "push"], cwd=repo_path)
    with pytest.raises(GitCommandFailedError):
        validate_git_command_expected_failure(result, "git push without upstream set")

    assert "no upstream branch" in result.stderr or "fatal" in result.stderr
    git_logger.info("Confirmed: 'git push' fails without upstream/tracking branch set.")

@pytest.mark.error_flow
@pytest.mark.infra
def test_invalid_git_command_raises_custom_exception(tmp_path):
    """
    Send a clearly invalid git command and expect InvalidGitCommandError to be raised.
    """
    command = ["git", "nonexistent"]
    result = run_git_command(command, cwd=tmp_path)
    
    with pytest.raises(InvalidGitCommandError) as exc_info:
        validate_git_command_expected_failure(result, " ".join(command))
    
    git_logger.info(f"Caught expected InvalidGitCommandError: {exc_info.value}")
