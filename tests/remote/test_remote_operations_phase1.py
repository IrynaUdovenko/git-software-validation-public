import re

import pytest

from logging_config import loggers
from utils.helpers import run_git_command
from utils.validators import (
    validate_git_command_success,
    assert_git_dir_structure_valid,
    assert_with_log,
)

git_logger = loggers["git_test"]


def validate_clients_commits(client1_local_repo_path, client2_local_repo_path):
    """
    Validate that both clients have the same commit after a push operation.
    This function checks that the HEAD commit of both client repositories
    matches after a push operation from client 1 to the remote bare repository.
    """
    # Get latest commit hash on both sides
    client1_commit = run_git_command(["git", "rev-parse", "HEAD"], cwd=client1_local_repo_path).stdout.strip()
    client2_commit = run_git_command(["git", "rev-parse", "HEAD"], cwd=client2_local_repo_path).stdout.strip()

    assert client1_commit == client2_commit, (
        f"Client2 did not receive the latest commit. " f"Client1 HEAD: {client1_commit}, Client2 HEAD: {client2_commit}"
    )


@pytest.mark.phase1
@pytest.mark.remote
def test_git_clone_from_bare_repo(git_bare_server, git_client_path):
    """
    Verify that 'git clone' from a bare repo creates a valid working copy.

    Clones from the newly created bare repo to a new client path and checks that
    the .git structure is valid.
    """
    remote_repo_path = git_bare_server
    clone_path = git_client_path

    result = run_git_command(["git", "clone", str(remote_repo_path), str(clone_path)], cwd=clone_path.parent)
    validate_git_command_success(result, f"git clone {remote_repo_path} {clone_path}")
    git_logger.info(f"Successfully cloned from {remote_repo_path} to {clone_path}")

    git_dir = clone_path / ".git"
    assert_git_dir_structure_valid(git_dir)

    git_logger.info(f"Validated structure of .git directory after clone: {git_dir}")


@pytest.mark.phase1
@pytest.mark.remote
def test_git_remote_add_origin_writes_to_config(git_init_repo, git_bare_server):
    """
    Verify that 'git remote add' correctly writes the remote URL to the .git/config file.

    This is tested via direct inspection of the config file.
    """
    repo_path = git_init_repo
    remote_path = git_bare_server

    remote_name = "origin"

    # Add remote
    result = run_git_command(["git", "remote", "add", remote_name, str(remote_path)], cwd=repo_path)
    validate_git_command_success(result, f"git remote add {remote_name} {remote_path}")

    # Validate .git/config
    config_path = repo_path / ".git" / "config"
    assert config_path.exists(), ".git/config not found"

    config_content = config_path.read_text()
    git_logger.debug(f"Config content:\n{config_content}")

    assert f'[remote "{remote_name}"]' in config_content, f'Remote section for "{remote_name}" not found in config'

    # Normalize config content: replace all backslashes with slashes
    normalized_config = re.sub(r"\\+", "/", config_content)
    expected_url = remote_path.as_posix()  # Convert to POSIX path (with '/') for consistency
    assert expected_url in normalized_config, f"URL for remote '{remote_name}' not found or incorrect in config"
    git_logger.info(f"Verified that remote '{remote_name}' points to {remote_path} in .git/config")


@pytest.mark.phase1
@pytest.mark.remote
def test_git_push_to_bare_repo(git_bare_server, local_repo_with_commit):
    """
    Verify that a client can push to a bare remote repository.
    """
    client_repo = local_repo_with_commit
    remote_path = git_bare_server

    # Add remote
    result = run_git_command(["git", "remote", "add", "origin", str(remote_path)], cwd=client_repo)
    validate_git_command_success(result, f"git remote add origin {str(remote_path)}")
    git_logger.info("Added remote 'origin' to client repo.")

    # Push to remote
    result = run_git_command(["git", "push", "-u", "origin", "main"], cwd=client_repo)
    validate_git_command_success(result, "git push -u origin main")
    git_logger.info("Pushed to remote origin.")

    # Get commit hash locally
    local_hash_result = run_git_command(["git", "rev-parse", "HEAD"], cwd=client_repo)
    validate_git_command_success(local_hash_result, "git rev-parse HEAD (local)")
    local_commit_hash = local_hash_result.stdout.strip()

    # Check remote HEAD
    head_path = remote_path / "refs" / "heads" / "main"
    assert_with_log(head_path.exists(), "Remote HEAD (refs/heads/main) not found", git_logger)

    remote_commit_hash = head_path.read_text().strip()
    assert_with_log(
        remote_commit_hash == local_commit_hash,
        "Remote commit hash does not match local HEAD after push",
        git_logger,
    )

    git_logger.info("Verified that pushed commit is present in remote repo.")


@pytest.mark.remote
@pytest.mark.phase1
def test_git_pull_fast_forward(
    git_bare_server,
    git_client_path,
    make_local_repo_and_push_factory,
):
    """
    Validates that 'git pull' performs a fast-forward update correctly.

    Flow:
    1. Server repo is created (bare).
    2. Client 2 clones the server repo before any commits are pushed (empty state).
    3. Client 1 pushes a new commit to the server.
    4. Client 2 performs 'git pull' and receives that commit.
    5. Validate that the commit hash in client 2 matches what was pushed by client 1.
    """

    remote_repo_path = git_bare_server
    client2_local_repo_path = git_client_path

    # Set global default branch to 'main' in client2 before cloning
    result = run_git_command(
        ["git", "config", "--global", "init.defaultBranch", "main"],
        cwd=client2_local_repo_path.parent,
    )
    validate_git_command_success(result, "git config init.defaultBranch main")

    # Step 1: Clone the bare repo as client 2 (before any commits)
    result = run_git_command(
        ["git", "clone", str(remote_repo_path), str(client2_local_repo_path)],
        cwd=client2_local_repo_path.parent,
    )
    validate_git_command_success(result, "git clone for client 2")
    git_logger.info("Client 2 succesfully cloned bare empty repo.")

    # Step 2: Client 1 pushes commit to the server
    client1_local_repo_path = make_local_repo_and_push_factory(remote_repo_path)
    git_logger.info("Client 1 succesfully pushed changes to bare empty repo.")

    # Step 3: Client 2 performs 'git pull'
    result = run_git_command(["git", "pull"], cwd=client2_local_repo_path)
    validate_git_command_success(result, "git pull")
    git_logger.info("Client 2 successfully pulled changes from remote bare repo.")

    # Step 4: Get latest commit hash on both sides
    validate_clients_commits(client1_local_repo_path, client2_local_repo_path)

    git_logger.info("Client 2 successfully pulled client´s 1 commit from remote repo.")


@pytest.mark.remote
@pytest.mark.phase1
@pytest.mark.smoke
def test_git_minimal_smoke_remote_flow(
    git_client_path,
    make_cloned_repo_and_push_factory,
    git_bare_server,
):
    """
    Validates full minimal remote Git flow:
    Client 1 clones → commits → pushes;
    Client 2 clones → verifies commit.

    Flow:
    1. Create bare server repo.
    2. Client 1 clones, commits, and pushes to it.
    3. Client 2 clones the updated repo.
    4. Validate that Client 2 sees the same commit.
    """

    remote_repo_path = git_bare_server

    # Step 1: Client 1 clones and pushes a commit to the server
    client1_local_repo_path, _ = make_cloned_repo_and_push_factory(remote_repo_path)
    git_logger.info("Client 1 successfully pushed a commit to remote repo.")

    # Step 2: Client 2 clones the remote after Client 1's push
    client2_local_repo_path = git_client_path.parent / "git-client-2"
    client2_local_repo_path.mkdir()

    result = run_git_command(
        ["git", "clone", str(remote_repo_path), str(client2_local_repo_path)],
        cwd=client2_local_repo_path.parent,
    )
    validate_git_command_success(result, "git clone by client 2")
    git_logger.info("Client 2 successfully cloned the updated remote repo.")

    # Step 3: Verify Client 2 has the latest commit
    validate_clients_commits(client1_local_repo_path, client2_local_repo_path)

    git_logger.info("Client 2 successfully sees the same commit as client 1 performed.")
