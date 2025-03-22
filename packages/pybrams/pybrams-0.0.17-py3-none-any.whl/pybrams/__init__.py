from .brams import adsb, file, location, system
from . import brams, event, optical, processing, trajectory, utils
import logging
import sys

__all__ = [
    "brams",
    "event",
    "optical",
    "processing",
    "trajectory",
    "utils",
    "adsb",
    "file",
    "location",
    "system",
    "enable_logging",
    "disable_logging",
    "enable_cache",
    "disable_cache",
    "clear_cache",
]

logging.basicConfig(
    stream=sys.stdout,
    level=logging.CRITICAL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_logging(level=logging.DEBUG) -> None:

    logging.getLogger().setLevel(level)


def disable_logging() -> None:

    logging.getLogger().setLevel(logging.CRITICAL)


def enable_cache() -> None:

    from pybrams.utils import Cache

    Cache.use_cache = True


def disable_cache() -> None:

    from pybrams.utils import Cache

    Cache.use_cache = False


def clear_cache(metadata_only: bool = False) -> None:

    from pybrams.utils import Cache

    Cache.clear(metadata_only)
