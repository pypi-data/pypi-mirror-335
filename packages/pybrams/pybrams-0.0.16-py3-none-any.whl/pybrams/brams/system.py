from dataclasses import dataclass
import json
import datetime
from typing import Union, Dict, Optional, List, TypedDict, Any

from .location import Location, get as get_location
from pybrams.brams.fetch import api
from pybrams.utils import Cache
from pybrams.utils import Config

api_endpoint = Config.get(__name__, "api_endpoint")


class SystemDict(TypedDict):
    system_code: str
    name: str
    start: str
    end: str
    antenna: int
    location_url: str
    location_code: str


@dataclass
class System:
    system_code: str
    name: str
    start: str
    end: str
    antenna: int
    location_url: str
    location_code: str

    def json(self) -> Dict[str, Any]:
        return {
            "system_code": self.system_code,
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "antenna": self.antenna,
            "location_url": self.location_url,
            "location_code": self.location_code,
        }

    @property
    def location(self) -> Location:
        return get_location(self.location_code)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, System) and self.system_code == other.system_code


def get(
    system_code: Optional[str] = None, location: Optional[Union[str, Location]] = None
) -> Dict[str, System]:
    if location:
        location_code = (
            location if isinstance(location, str) else location.location_code
        )
        cached_systems = Cache.get("systems")

        if cached_systems:
            all_systems = json.loads(cached_systems).get("data")
            matching_systems = {
                system_code: system
                for system_code, system in all_systems.items()
                if system["location_code"] == location_code
            }

        else:
            payload = {"location_code": location_code}
            response = api.request(api_endpoint, payload)
            api_response: Union[SystemDict, List[SystemDict]] = (
                response.json() if response else []
            )

            if isinstance(api_response, dict):
                matching_systems = {api_response["system_code"]: System(**api_response)}

            else:
                matching_systems = {
                    system["system_code"]: System(**system) for system in api_response
                }

            for system_code, system in matching_systems.items():
                json_content = {
                    "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                    "data": {system_code: system.json()},
                }

                Cache.cache(system_code, json.dumps(json_content, indent=4))

        return matching_systems

    elif system_code:
        system = {}

        for key in [system_code, "systems"]:
            json_system = Cache.get(key)

            if json_system:
                system = json.loads(json_system).get("data").get(system_code)

                if system:
                    break

        if not system:
            payload = {"system_code": system_code}

            response = api.request(api_endpoint, payload)
            json_system = response.json()

            json_content = {
                "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                "data": {system_code: json_system},
            }

            Cache.cache(system_code, json.dumps(json_content, indent=4))
            system = json_system

            if not system:
                raise ValueError(f"Invalid system code: {system_code}")

        s = System(*system.values())
        return {s.system_code: s}

    else:
        raise ValueError("No location or system code was provided")


def all() -> Dict[str, System]:
    json_systems = Cache.get("systems")

    if not json_systems:
        response = api.request(api_endpoint)
        json_systems = {system["system_code"]: system for system in response.json()}

        json_content = {
            "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "data": json_systems,
        }

        Cache.cache("systems", json.dumps(json_content, indent=4))

    else:
        json_systems = json.loads(json_systems).get("data")

    systems: dict[str, System] = {}

    for code, json_system in json_systems.items():
        systems[code] = System(*json_system.values())

    return systems
