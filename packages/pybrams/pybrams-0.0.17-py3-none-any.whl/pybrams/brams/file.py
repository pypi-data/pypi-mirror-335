from __future__ import annotations
from abc import ABC
from typing import Any, Dict, Optional, Union, List
from collections.abc import KeysView, ValuesView
import os
import json
import hashlib
import datetime

from pybrams.utils import Config
import pybrams.brams.location
import pybrams.brams.system
from pybrams.brams.formats.wav import Metadata, Wav
from pybrams.processing.signal import Signal
from pybrams.brams.fetch import api, archive
from pybrams.utils import http
from pybrams.utils import Cache
from pybrams.utils.interval import Interval
import logging

logger = logging.getLogger(__name__)

use_brams_archive = False

api_endpoint = Config.get(__name__, "api_endpoint")


class AbstractFile(ABC):
    def __init__(
        self,
        samplerate: float,
        pps_count: int,
        duration: int,
        start: datetime.datetime,
        end: datetime.datetime,
        system: pybrams.brams.system.System,
        location: pybrams.brams.location.Location,
        type: str,
        signal_properties: Optional[dict[str, Any]],
    ) -> None:
        super().__init__()

        self.samplerate: float = samplerate
        self.pps_count: int = pps_count
        self.duration: int = duration
        self.start: datetime.datetime = start
        self.end: datetime.datetime = end
        self.system: pybrams.brams.system.System = system
        self.location: pybrams.brams.location.Location = location
        self.signal_properties: Optional[dict[str, Any]] = signal_properties
        self.type: str = type
        self._signal: Optional[Signal] = None

    @property
    def signal(self) -> Signal:
        if self._signal is None:
            raise ValueError(
                "The file needs to be loaded before accessing the signal property"
            )

        return self._signal

    def __str__(self) -> str:
        return (
            f"File(samplerate={self.samplerate} Hz, pps_count={self.pps_count}, "
            f"duration={self.duration}s, start={self.start}, end={self.end}, "
            f"system={self.system}, location={self.location}, "
            f"signal_properties={self.signal_properties})"
        )


class SyntheticFile(AbstractFile):
    def __init__(
        self,
        samplerate: float,
        pps_count: int,
        duration: int,
        start: datetime.datetime,
        end: datetime.datetime,
        system: pybrams.brams.system.System,
        location: pybrams.brams.location.Location,
        ftype: str,
        signal_properties: Optional[dict[str, Any]],
    ) -> None:
        super().__init__(
            samplerate,
            pps_count,
            duration,
            start,
            end,
            system,
            location,
            ftype,
            signal_properties,
        )


class File(AbstractFile):
    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hours: int,
        minutes: int,
        samplerate: float,
        pps_count: int,
        duration: int,
        precise_start: int,
        precise_end: int,
        system_code: str,
        location_code: str,
        location_url: str,
        system_url: str,
        wav_url: str,
        wav_name: str,
        png_url: str,
        png_name: str,
        signal_properties: Optional[dict[str, Any]] = None,
    ) -> None:
        self.year: int = year
        self.month: int = month
        self.day: int = day
        self.hours: int = hours
        self.minutes: int = minutes
        self.date = datetime.datetime(
            self.year, self.month, self.day, self.hours, self.minutes
        )
        self.precise_start = precise_start
        self.precise_end = precise_end
        self.system_code = system_code
        self.location_code = location_code
        self.location_url: str = location_url
        self.system_url: str = system_url
        self.wav_url: str = wav_url
        self.wav_name: str = wav_name
        self.png_url: str = png_url
        self.png_name: str = png_name

        self.corrected_wav_name = f"{self.wav_name[:-4]}.corrected.wav"
        self.cleaned_wav_name = f"{self.wav_name[:-4]}.cleaned.wav"
        ftype = (
            "AR"
            if "BEHUMA" in self.system_code
            else "RSP2" if samplerate == 6048 else "ICOM"
        )
        self._metadata: Optional[Metadata] = None

        start = datetime.datetime.fromtimestamp(
            precise_start / 1e6, tz=datetime.timezone.utc
        )
        end = datetime.datetime.fromtimestamp(
            precise_end / 1e6, tz=datetime.timezone.utc
        )

        system = pybrams.brams.system.get(self.system_code)[self.system_code]
        location = pybrams.brams.location.get(self.location_code)

        super().__init__(
            samplerate,
            pps_count,
            duration,
            start,
            end,
            system,
            location,
            ftype,
            signal_properties,
        )

    @property
    def metadata(self) -> Metadata:
        if self._metadata is None:
            raise ValueError(
                "The file needs to be loaded before accessing the metadata property"
            )

        return self._metadata

    def json(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hours": self.hours,
            "minutes": self.minutes,
            "sample_rate": self.samplerate,
            "pps_count": self.pps_count,
            "duration": self.duration,
            "precise_start": self.precise_start,
            "precise_end": self.precise_end,
            "system_code": self.system_code,
            "location_code": self.location_code,
            "location_url": self.location_url,
            "system_url": self.system_url,
            "wav_url": self.wav_url,
            "wav_name": self.wav_name,
            "png_url": self.png_url,
            "png_name": self.png_name,
            "signal_properties": self._signal.json() if self._signal else None,
        }

    def load(self) -> None:
        logger.info(f"Loading file {self.wav_name}")
        wav_content = Cache.get(self.wav_name, False)

        if use_brams_archive:
            wav_content = archive.get(
                self.system_code,
                self.year,
                self.month,
                self.day,
                self.hours,
                self.minutes,
            )

        if not wav_content:
            while not wav_content or not len(wav_content):
                response = http.get(self.wav_url)
                wav_content = getattr(response, "content", None)

            Cache.cache(self.wav_name, wav_content, False)

        self._metadata, series, pps = Wav.read(wav_content)
        self._signal = Signal(
            series, pps, self.samplerate, self.system, self.type, self.signal_properties
        )

    def save(self, path: str = ".") -> None:
        logger.info(f"Saving file {self.wav_name}")
        self.load() if not self._signal else None

        with open(os.path.join(path, self.wav_name), "wb") as file:
            file.write(Wav.write(self.metadata, self.signal.series, self.signal.pps))

    def process(self) -> None:
        logger.info(f"Processing file {self.wav_name}")
        corrected_wav_content = Cache.get(self.corrected_wav_name, False)
        self.load() if self._signal is None else None

        if not corrected_wav_content:
            self.signal.process()
            corrected_wav_content = Wav.write(
                self.metadata, self.signal.series, self.signal.corrected_pps
            )
            Cache.cache(self.json_string(), json.dumps(self.json(), indent=4))
            Cache.cache(self.corrected_wav_name, corrected_wav_content, False)

        else:
            _, _, self.signal._corrected_pps = Wav.read(corrected_wav_content)

    def clean(self) -> None:
        cleaned_wav_content = Cache.get(self.cleaned_wav_name, False)
        self.load() if self._signal is None else None

        if not cleaned_wav_content:
            self.process() if (self.signal._corrected_pps is None) else None
            logger.info(f"Cleaning file {self.wav_name}")
            self._signal.clean() if self._signal else None
            cleaned_wav_content = Wav.write(
                self.metadata, self._signal._cleaned_series, self.signal.corrected_pps
            )
            Cache.cache(self.cleaned_wav_name, cleaned_wav_content, False)

        else:
            self._metadata, self.signal._cleaned_series, self.signal._corrected_pps = (
                Wav.read(cleaned_wav_content)
            )
            self.signal.beacon_frequency = self.signal_properties["beacon_frequency"]

    def json_string(self) -> str:
        return f"{self.system_code}.{str(self.year).zfill(4)}{str(self.month).zfill(2)}{str(self.day).zfill(2)}_{str(self.hours).zfill(2)}{str(self.minutes).zfill(2)}"

    def __add__(self, other: object) -> SyntheticFile:
        if not isinstance(other, File):
            raise TypeError(
                f"Unsupported operand type(s) for +: File and {type(other).__name__}"
            )
        if self.system_code != other.system_code:
            raise ValueError(
                "Adding File objects from different systems is not supported"
            )

        if self.type != other.type:
            raise ValueError(
                "Adding File objects with different types is not supported"
            )

        import autograd.numpy as np

        samplerate = np.mean([self.samplerate, other.samplerate])
        pps_count = self.pps_count + other.pps_count
        duration = self.duration + other.duration
        start = self.start if self.start < other.start else other.start
        end = self.end if self.end > other.end else other.end
        file = SyntheticFile(
            samplerate,
            pps_count,
            duration,
            start,
            end,
            self.system,
            self.location,
            self.type,
            {},
        )

        file._signal = (
            self.signal + other.signal if self._signal and other._signal else None
        )
        return file

    def __eq__(self, other: object) -> bool:
        if isinstance(other, File):
            return (
                self.year == other.year
                and self.month == other.month
                and self.day == other.day
                and self.hours == other.hours
                and self.minutes == other.minutes
                and self.samplerate == other.samplerate
                and self.pps_count == other.pps_count
                and self.duration == other.duration
                and self.precise_start == other.precise_start
                and self.precise_end == other.precise_end
                and self.system_code == other.system_code
                and self.location_code == other.location_code
                and self.location_url == other.location_url
                and self.system_url == other.system_url
                and self.wav_url == other.wav_url
                and self.wav_name == other.wav_name
                and self.png_url == other.png_url
                and self.png_name == other.png_name
                and self.corrected_wav_name == other.corrected_wav_name
                and self.type == other.type
                and self._signal == other._signal
            )

        return False


def get(
    interval: Union[Interval, datetime.datetime],
    system: Union[
        str,
        pybrams.brams.system.System,
        List[Union[str, pybrams.brams.system.System]],
        KeysView,
        ValuesView,
        None,
    ] = None,
    *,
    load: bool = False,
    save: bool = False,
    process: bool = False,
    clean: bool = False,
) -> Dict[str, List[File]]:
    def generate_key(payload: Dict[str, Any]) -> str:
        result: list = []
        for key in sorted(payload.keys()):
            value = payload[key]
            if isinstance(value, datetime.datetime):
                result.append(f"{key}{value.strftime('%Y%m%d_%H%M')}")
            if isinstance(value, list):
                joined_list = "-".join(value)
                if joined_list:
                    result.append(joined_list)

        return hashlib.sha256(("_".join(result)).encode()).hexdigest()

    def normalize_systems(
        system: Union[
            str,
            pybrams.brams.system.System,
            List[Union[str, pybrams.brams.system.System]],
            KeysView,
            ValuesView,
            None,
        ],
    ) -> List[str]:
        system_list: List[str] = []

        if isinstance(system, str):
            system_list.append(system)

        elif isinstance(system, pybrams.brams.system.System):
            system_list.append(system.system_code)

        elif isinstance(system, list) or isinstance(system, (KeysView, ValuesView)):
            items: list = list(system) if not isinstance(system, list) else system

            if all(isinstance(item, str) for item in items):
                system_list.extend(items)
            elif all(isinstance(item, pybrams.brams.system.System) for item in items):
                system_list.extend(s.system_code for s in items)
            else:
                raise ValueError(
                    "List contains mixed types. Expected all strings or all systems.System instances."
                )

        elif system is None:
            pass
        else:
            raise TypeError("Unsupported type for 'system' parameter")

        return system_list

    files: Dict[str, List[File]] = {}
    system_list = normalize_systems(system)

    if isinstance(interval, Interval):
        payload = {
            "from": interval.start,
            "to": interval.end,
            "system_code[]": system_list,
        }

    elif isinstance(interval, datetime.datetime):
        payload = {
            "start": interval,
            "system_code[]": system_list,
        }

    else:
        raise TypeError("Unsupported type for 'interval' parameter")

    key = generate_key(payload)
    cached_response = Cache.get(key)

    if cached_response:
        json_response = json.loads(cached_response)
    else:
        response = api.request(api_endpoint, payload)

        if not response:
            logging.error("No response from API")
            return {}
        json_response = response.json()
        Cache.cache(key, json.dumps(json_response, indent=4))

        if not json_response:
            raise ValueError("No file was found with this interval and system(s)")

    for file in json_response:
        system_code = file.get("system_code")
        key = f"{system_code}.{file.get('year'):04}{file.get('month'):02}{file.get('day'):02}_{file.get('hours'):02}{file.get('minutes'):02}"
        cached_file = Cache.get(key)

        if cached_file:
            f = File(*json.loads(cached_file).values())
            f.load() if load else None
            f.save() if save else None
            f.process() if process else None
            f.clean() if clean else None
            files.setdefault(system_code, []).append(f)

        else:
            f = File(*file.values())
            f.load() if load else None
            f.save() if save else None
            f.process() if process else None
            f.clean() if clean else None
            files.setdefault(system_code, []).append(f)
            Cache.cache(key, json.dumps(f.json(), indent=4))

    return files
