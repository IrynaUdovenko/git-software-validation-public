import re

import pytest

from logging_config import loggers
from utils.helpers import run_git_command
from utils.validators import assert_git_command_success, assert_with_log

git_logger = loggers["git_test"]


@pytest.mark.phase1
@pytest.mark.setup
def test_git_config_sets_username_and_email(git_init_repo, set_git_user_config):
    """
    Verify that 'git config' sets user.name and user.email correctly.

    Uses the fixture-factory to configure user.name and user.email locally,
    then reads the .git/config file directly to verify that the values were written correctly.
    """
    username = "Test User"
    email = "test@example.com"

    # Apply local config using fixture-factory
    set_git_user_config(git_init_repo, username=username, email=email)

    git_logger.info("Configured user.name and user.email using fixture")

    # Directly read .git/config to verify values
    config_path = git_init_repo / ".git" / "config"
    config_text = config_path.read_text()
    git_logger.debug(f"Read .git/config content:\n{config_text}")

    assert f"name = {username}" in config_text, f"user.name '{username}' not found in config"
    assert f"email = {email}" in config_text, f"user.email '{email}' not found in config"

    git_logger.info("Verified that user.name and user.email were correctly written to .git/config")


@pytest.mark.phase1
@pytest.mark.setup
def test_git_config_sets_default_branch_to_main(tmp_path):
    """
    Verify that 'git config --global init.defaultBranch main' correctly sets the initial branch to 'main'.

    Instead of using 'git branch', which is reserved for Phase 2, we inspect the .git/HEAD file.
    """

    # Set default branch to 'main' globally
    result = run_git_command(["git", "config", "--global", "init.defaultBranch", "main"], cwd=tmp_path)
    assert_git_command_success(result, "git config --global init.defaultBranch main")

    # Init repo
    result = run_git_command(["git", "init"], cwd=tmp_path)
    assert_git_command_success(result, "git init")

    # Read .git/HEAD
    head_file = tmp_path / ".git" / "HEAD"
    assert head_file.exists(), ".git/HEAD does not exist"

    head_content = head_file.read_text().strip()
    git_logger.debug(f".git/HEAD content: {head_content}")

    assert head_content == "ref: refs/heads/main", f"Expected HEAD to point to 'main', but got: {head_content}"

    git_logger.info("Confirmed that HEAD points to 'refs/heads/main' after setting init.defaultBranch globally.")


@pytest.mark.phase1
@pytest.mark.setup
@pytest.mark.integration
def test_git_config_local_overrides_global(set_git_user_config, request):
    """
    Sets global config first, then gets repo with local config & commit,
    to verify that local overrides global in Git behavior.
    """

    # Set global config first
    set_git_user_config(repo_path=None, username="Global User", email="global@example.com", global_=True)

    # Get repo with local config and commit
    repo_path = request.getfixturevalue("local_repo_with_commit")

    # Get commit hash
    result = run_git_command(["git", "rev-parse", "HEAD"], cwd=repo_path)
    assert_git_command_success(result, "git rev-parse HEAD")
    commit_hash = result.stdout.strip()

    # Show raw commit object
    result = run_git_command(["git", "cat-file", "-p", commit_hash], cwd=repo_path)
    assert_git_command_success(result, f"git cat-file -p {commit_hash}")
    commit_content = result.stdout

    # Check author line
    expected_author = "Local User <local@example.com>"
    match = re.search(r"^author\s+(.+?\s<.+?>)", commit_content, re.MULTILINE)
    actual_author = match.group(1) if match else "<not found>"
    assert_with_log(
        expected_author in commit_content,
        f"Failed! Expected author : {expected_author}, actual author: {actual_author}",
        git_logger,
    )
    git_logger.info("Verified local config overrides global in commit author (via raw commit object).")
