import pytest
import time

from logging_config import loggers

# get infra logger for infrastructure-related logs
infra_logger = loggers["infra"]

@pytest.hookimpl()
def pytest_sessionstart(session):
    session.config._start_time = time.time()
    infra_logger.info("=========================== Pytest session started ==================")

@pytest.hookimpl()
def pytest_sessionfinish(session, exitstatus):
    duration = time.time() - session.config._start_time
    infra_logger.info(f"================== Pytest session finished in {duration:.2f} seconds ======================")