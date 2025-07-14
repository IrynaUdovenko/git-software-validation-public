import subprocess
from pathlib import Path

import pytest

from logging_config import loggers

infra_logger = loggers["infra"]


def create_temp_files_in_repo(repo_path: Path, filenames: list[str]) -> list[Path]:
    """
    Create one or more temporary files inside the given Git repository path.

    Each file will be filled with simple sample content.

    Parameters:
    - repo_path: Path to the initialized Git repo.
    - filenames: List of file names to create.

    Returns:
    - List of full Path objects pointing to the created files.
    """
    created_files = []

    for name in filenames:
        file_path = repo_path / name
        file_path.write_text(f"This is test content for {name}\n")
        infra_logger.debug(f"Created file: {file_path} in repo : {repo_path}")
        assert file_path.exists(), f"Failed to create file: {file_path}"
        created_files.append(file_path)

    return created_files


def run_git_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """
    Run a Git command with logging, and return the result.

    Does NOT raise on failure — caller is responsible for checking returncode.
    Catches and logs system-level errors like invalid directory or missing git.

    Parameters:
    - command: The Git command to run as a list of arguments.
    - cwd: The working directory to run the command in.

    Returns:
    - subprocess.CompletedProcess: Contains returncode, stdout, stderr.
      If an exception is raised during execution, returns a dummy result with code 1.
    """
    infra_logger.debug(f"Running command: {' '.join(command)} in {cwd}")
    try:
        infra_logger.debug(f"Running command: {' '.join(command)} in {cwd}")
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        infra_logger.debug(f"Return code: {result.returncode}")
        infra_logger.debug(f"Return stderr: {result.stderr.strip()}")

        return result

    except Exception as e:
        infra_logger.error(f"Failed to run command: {' '.join(command)} in {cwd}")
        infra_logger.error(f"Exception: {type(e).__name__} - {e}")
        raise
