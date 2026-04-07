import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger for the entire application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )
