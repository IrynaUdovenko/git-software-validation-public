import pytest
from logging_config import loggers

infra_logger = loggers["infra"]
git_logger = loggers["git_test"]
api_logger = loggers["api_test"]

# Global map: nodeid -> list of markers
_nodeid_to_markers = {}


@pytest.hookimpl
def pytest_collection_modifyitems(session, config, items):
    """Collect markers for each test item and store them in a global map."""
    global _nodeid_to_markers
    _nodeid_to_markers = {}
    for item in items:
        markers = [m.name for m in item.iter_markers()]
        _nodeid_to_markers[item.nodeid] = markers


def _pick_logger(nodeid: str):
    """Select the appropriate logger based on stored markers."""
    markers = _nodeid_to_markers.get(nodeid, [])
    if "phase1" in markers:
        return git_logger
    elif "phase2" in markers:
        return api_logger
    else:
        return infra_logger


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logstart(nodeid, location):
    """Log the start of a test with the appropriate logger."""
    logger = _pick_logger(nodeid)
    logger.info(f"=========== START TEST: {nodeid} ===========")
    infra_logger.info(f"=========== START TEST: {nodeid} ===========")


@pytest.hookimpl()
def pytest_runtest_logreport(report):
    """Log the outcome of each test phase with the appropriate logger."""
    logger = _pick_logger(report.nodeid)
    phase = report.when
    nodeid = report.nodeid

    if report.failed:
        logger.error(f"TEST {phase.upper()} FAILED: {nodeid}")
        if hasattr(report.longrepr, "reprcrash"):
            logger.error(report.longrepr.reprcrash.message)
        else:
            logger.error(f"Traceback:\n{report.longrepr}")
    elif report.passed and phase == "call":
        logger.info(f"TEST PASSED: {nodeid}")
    elif report.skipped:
        logger.warning(f"TEST {phase.upper()} SKIPPED: {nodeid}")
