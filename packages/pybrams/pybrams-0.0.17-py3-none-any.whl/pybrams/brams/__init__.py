from pybrams.brams.fetch.archive import is_archive_reachable
from . import adsb
from . import location
from . import system
from . import file
from . import formats
from . import fetch

__all__ = ["adsb", "location", "system", "file", "formats", "fetch"]


def enable_brams_archive() -> None:

    file.use_brams_archive = is_archive_reachable()


def disable_brams_archive() -> None:

    file.use_brams_archive = False
