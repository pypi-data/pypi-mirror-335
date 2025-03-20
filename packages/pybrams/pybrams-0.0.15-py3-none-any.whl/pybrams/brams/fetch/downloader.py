from typing import Dict, Any, Optional
from pybrams.utils.http import get
import requests
import logging

logger = logging.getLogger(__name__)

base_url = "https://brams.aeronomie.be/downloader.php"


def request(payload: Optional[Dict[str, Any]] = None) -> requests.Response:
    logger.debug(f"Calling downloader with payload {payload}")
    return get(base_url, payload)
