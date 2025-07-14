import logging
from pathlib import Path


def setup_logging(log_dir: Path = Path("logs")):
    """
    Configure multiple loggers for different parts of the project with both console and file handlers.
    Each logger can have a different logging level.

    Parameters:
    - log_dir: Path to the directory where log files will be stored.
    """

    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s @ %(module)s:%(lineno)d]: %(message)s")

    # Console handler (for terminal output)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Logger configuration: name -> (description, level)
    logger_configs = {
        "git_test": ("Git core functionality tests", logging.INFO),
        "infra": ("Environment and setup", logging.DEBUG),
        "auth": ("Authentication handling", logging.WARNING),
        "client_sim": ("Client-side Git operations", logging.INFO),
        "ci": ("CI pipeline logging", logging.DEBUG),
    }

    loggers = {}

    for name, (description, level) in logger_configs.items():
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Avoid duplicate handlers if called multiple times
        if not logger.handlers:
            # File handler for writing logs to separate files
            file_handler = logging.FileHandler(log_dir / f"{name}.log", mode="w")
            file_handler.setFormatter(formatter)

            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        loggers[name] = logger

    return loggers


# Initialize loggers when this module is imported
loggers = setup_logging()
