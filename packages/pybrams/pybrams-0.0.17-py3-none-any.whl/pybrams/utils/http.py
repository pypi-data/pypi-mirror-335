from typing import Dict, Any, Optional
import requests
import logging
from urllib.parse import urlparse
from pybrams.utils import Config

logger = logging.getLogger(__name__)


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if not parsed.scheme or parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")


def get(url: str, payload: Optional[Dict[str, Any]] = None) -> requests.Response:
    validate_url(url)

    logger.debug(f"Getting {url} with payload {payload}")
    max_retries = Config.get(__name__, "max_retries")
    timeout = Config.get(__name__, "timeout")
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, timeout=timeout, params=payload)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {retries + 1} failed for {url}. Error: {e}")
            retries += 1

    logger.error(f"Failed to GET {url} after {max_retries} attempts")
    raise requests.exceptions.RequestException(
        f"Failed to GET {url} after {max_retries} attempts"
    )


def post(url: str, payload: Optional[Dict[str, Any]] = None) -> requests.Response:
    validate_url(url)

    logger.debug(f"Posting {url} with payload {payload}")
    max_retries = Config.get(__name__, "max_retries")
    timeout = Config.get(__name__, "timeout")

    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(url, data=payload, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {retries + 1} failed for {url}. Error: {e}")
            retries += 1

    logger.error(f"Failed to POST {url} after {max_retries} attempts")
    raise requests.exceptions.RequestException(
        f"Failed to POST {url} after {max_retries} attempts"
    )
