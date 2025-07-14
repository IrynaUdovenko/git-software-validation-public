import pytest

from logging_config import loggers

# Get the loggers for different parts of the project
infra_logger = loggers["infra"]
git_logger = loggers["git_test"]


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logstart(nodeid, location):
    """
    Log the beginning of each test case using our custom git_logger.
    """
    git_logger.info(f"=========== START TEST: {nodeid} ===========")
    infra_logger.info(f"=========== START TEST: {nodeid} ===========")


@pytest.hookimpl()
def pytest_runtest_logreport(report):
    """
    Log the result of each test phase (setup, call, teardown).
    Shows detailed info on failure for better debugging.
    """
    phase = report.when
    nodeid = report.nodeid

    if report.failed:
        git_logger.error(f"TEST {phase.upper()} FAILED: {nodeid}")
        if hasattr(report.longrepr, "reprcrash"):
            git_logger.error(f"{report.longrepr.reprcrash.message}")
        else:
            git_logger.error(f"Traceback:\n{str(report.longrepr)}")
    elif report.passed and phase == "call":
        git_logger.info(f"TEST PASSED: {nodeid}")
    elif report.skipped:
        git_logger.warning(f"TEST {phase.upper()} SKIPPED: {nodeid}")
