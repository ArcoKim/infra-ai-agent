import logging
import sys

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure and return the application logger."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Create app logger
    logger = logging.getLogger("infra-ai-agent")
    logger.setLevel(log_level)

    return logger


# Singleton logger instance
logger = setup_logging()
