import os
from pybrams.brams.formats.zip import ZipExtractor
from pybrams.utils import Config
import logging

logger = logging.getLogger(__name__)

base_path = Config.get(__name__, "base_path")


def is_archive_reachable():

    if not os.path.exists(base_path) or not os.path.isdir(base_path):

        error_message = (
            f"BRAMS archive path does not exist or is not a directory: {base_path}"
        )
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    try:
        os.listdir(base_path)

    except PermissionError as e:
        error_message = (
            f"Permission denied: Cannot read the BRAMS archive directory: {base_path}"
        )
        logger.error(error_message)
        raise PermissionError(error_message) from e

    return True


def get(
    system_code: str, year: int, month: int, day: int, hours: int, minutes: int
) -> bytes:

    zip_name = f"RAD_BEDOUR_{year:04}{month:02}{day:02}_{hours:02}00_{system_code}.zip"
    wav_name = f"RAD_BEDOUR_{year:04}{month:02}{day:02}_{hours:02}{minutes:02}_{system_code}.wav"
    zip_path = os.path.join(
        base_path, system_code[:6], f"{year:04}", f"{month:02}", zip_name
    )

    return ZipExtractor(zip_path).extract_file(wav_name)
