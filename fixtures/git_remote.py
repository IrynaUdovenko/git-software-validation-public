from pathlib import Path
from typing import Callable

import pytest

from logging_config import loggers
from utils.helpers import run_git_command
from utils.validators import assert_git_command_success

# Get the loggers for different parts of the project
infra_logger = loggers["infra"]


@pytest.fixture
def make_cloned_repo_with_commit_factory(git_bare_server, git_client_path, commit_temp_file_with_local_config) -> Callable[[Path], tuple[Path, Path]]:
    """
    Factory fixture that clones a Git repository, sets local config,
    adds a file, stages it, and makes a commit.

    If a remote path is passed, it uses it.
    Otherwise, it creates a new bare server.

    Returns a callable that accepts an optional remote_repo_path,
    and returns (cloned_repo_path, remote_repo_path).
    """

    def _make(remote_repo_path: Path = None) -> tuple[Path, Path]:
        # If not provided, create a new bare server
        if remote_repo_path is None:
            remote_repo_path = git_bare_server

        client_path = git_client_path

        # Set global default branch before cloning
        result = run_git_command(
            ["git", "config", "--global", "init.defaultBranch", "main"],
            cwd=client_path.parent,
        )
        assert_git_command_success(result, "git config init.defaultBranch")

        # Clone the remote
        result = run_git_command(
            ["git", "clone", str(remote_repo_path), str(client_path)],
            cwd=client_path.parent,
        )
        assert_git_command_success(result, "git clone")
        infra_logger.info("Client successfully cloned remote repo and set default branch to 'main'.")

        # Apply local config + commit
        repo_path = commit_temp_file_with_local_config(client_path)
        return repo_path, remote_repo_path

    return _make


@pytest.fixture
def make_local_repo_and_push_factory(local_repo_with_commit) -> Callable[[Path, str, str], Path]:
    """
    Factory fixture that creates a repo (using git init), adds a remote, pushes initial commit to it.
    Pushes to remote using default 'origin' and branch 'main' or using passed args.
    remote_repo_path is the path to the remote bare repo.
    """

    def _make(remote_repo_path: Path, remote_name: str = "origin", branch_name: str = "main") -> Path:
        repo_path = local_repo_with_commit

        # Add remote
        result = run_git_command(["git", "remote", "add", remote_name, str(remote_repo_path)], cwd=repo_path)
        assert_git_command_success(result, f"git remote add {remote_name}")

        # Push commit
        result = run_git_command(["git", "push", "-u", remote_name, branch_name], cwd=repo_path)
        assert_git_command_success(result, f"git push to {remote_name}/{branch_name}")

        return repo_path

    return _make


@pytest.fixture
def make_cloned_repo_and_push_factory(
    make_cloned_repo_with_commit_factory,
) -> Callable[[Path, str, str], tuple[Path, Path]]:
    """
    Factory fixture that clones a repo, sets local config, commits a file,
    adds a remote, and pushes the commit to it.

    By default, creates a new bare server and uses 'origin' + 'main' as remote/branch.
    Can accept an existing remote path.

    Returns a callable that accepts:
    - remote_repo_path (optional): existing remote to use
    - remote_name: name of the remote (default: 'origin')
    - branch_name: branch to push to (default: 'main')
    """

    def _make(
        remote_repo_path: Path = None,
        remote_name: str = "origin",
        branch_name: str = "main",
    ) -> Path:
        repo_path, actual_remote_path = make_cloned_repo_with_commit_factory(remote_repo_path)

        # Add remote (if not already added)
        # result = run_git_command(
        #   ["git", "remote", "add", remote_name, str(actual_remote_path)],
        #  cwd=repo_path,
        # )
        # assert_git_command_success(result, f"git remote add {remote_name}")

        # Push commit
        result = run_git_command(["git", "push"], cwd=repo_path)
        assert_git_command_success(result, f"git push to {remote_name}/{branch_name}")

        return repo_path, actual_remote_path

    return _make


@pytest.fixture
def git_bare_server(tmp_path_factory) -> Path:
    """
    Creates a temporary bare Git repository as a remote server.
    """
    base_dir = tmp_path_factory.mktemp("remote_git_server")
    bare_repo_path = base_dir / "remote-repo.git"
    bare_repo_path.mkdir()
    result = run_git_command(["git", "init", "--bare"], cwd=bare_repo_path)
    assert_git_command_success(result, "git init --bare")

    # Set HEAD to main branch (otherwise it defaults to master)
    result = run_git_command(["git", "symbolic-ref", "HEAD", "refs/heads/main"], cwd=bare_repo_path)
    assert_git_command_success(result, "git symbolic-ref HEAD refs/heads/main")
    head_file = bare_repo_path / "HEAD"
    head_content = head_file.read_text().strip()
    assert head_content == "ref: refs/heads/main", f"Expected HEAD to point to main, got: {head_content}"

    infra_logger.info(f"Created bare Git repository at {bare_repo_path} with main branch set as default.")
    return bare_repo_path
