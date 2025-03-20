from typing import Dict, Any, Optional
import requests
from pybrams.utils.http import post
import logging

logger = logging.getLogger(__name__)
from pybrams.utils import Config

base_url = Config.get(__name__, "base_url")


def request(
    endpoint: str, payload: Optional[Dict[str, Any]] = None
) -> requests.Response:
    logger.debug(f"Calling API {endpoint} with payload {payload}")
    return post(base_url + endpoint, payload)
