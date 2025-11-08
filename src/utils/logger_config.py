import logging
from colorlog import ColoredFormatter

# Set up once and expose this logger
logger = logging.getLogger("atlas")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():  # prevent duplicate handlers
    handler = logging.StreamHandler()
    handler.setFormatter(
        ColoredFormatter(
            (
                "%(log_color)s%(asctime)s - %(name)s "
                "- %(levelname)s - %(message)s"
            ),
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )
    logger.addHandler(handler)
    logger.propagate = False

# Silence third-party libraries
for lib in [
    "openai",
    "azure",
    "httpcore",
    "httpx",
    "urllib3",
    "requests",
    "pypandoc",
]:
    logging.getLogger(lib).setLevel(logging.WARNING)

logging.getLogger("kernel").setLevel(logging.DEBUG)
