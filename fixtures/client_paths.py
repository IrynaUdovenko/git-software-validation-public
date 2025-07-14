import uuid
from pathlib import Path

import pytest

from logging_config import loggers

# Get the loggers for different parts of the project
infra_logger = loggers["infra"]
git_logger = loggers["git_test"]


@pytest.fixture
def git_client_path(tmp_path_factory) -> Path:
    """
    Provides a unique temporary directory simulating a Git client machine.
    Ensures no path collision on repeated use (e.g., clone operations).
    """
    unique_suffix = uuid.uuid4().hex[:8]
    client_path = tmp_path_factory.mktemp(f"git-client-{unique_suffix}")
    return client_path
