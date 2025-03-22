from typing import Any, Dict, Union, TypedDict, Optional
from dataclasses import dataclass
import json
import datetime

from pybrams.utils.coordinates import Coordinates
from pybrams.utils import Cache
from pybrams.brams.fetch import api
from pybrams.utils import Config

api_endpoint = Config.get(__name__, "api_endpoint")


class LocationDict(TypedDict):
    location_code: str
    name: str
    status: str
    longitude: float
    latitude: float
    altitude: int
    systems_url: str


@dataclass
class Location:
    location_code: str
    name: str
    status: str
    longitude: float
    latitude: float
    altitude: int
    systems_url: str

    def __post_init__(self):
        self.coordinates = Coordinates.fromGeodetic(
            self.latitude, self.longitude, self.altitude
        )

    def json(self) -> Dict[str, Any]:
        return {
            "location_code": self.location_code,
            "name": self.name,
            "status": self.status,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "altitude": self.altitude,
            "systems_url": self.systems_url,
        }

    @property
    def systems(self):
        from pybrams.brams.system import get as get_system

        return get_system(location=self)


def get(location_code: str) -> Location:
    location: Optional[LocationDict] = None

    for key in [location_code, "locations"]:
        json_location = Cache.get(key)

        if json_location:
            location = json.loads(json_location).get("data").get(location_code)

            if location:
                break

    if not location:
        payload = {"location_code": location_code}

        response = api.request(api_endpoint, payload)
        json_location = response.json()

        if any(json_location.keys()):
            json_content = {
                "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                "data": {location_code: json_location},
            }

            Cache.cache(location_code, json.dumps(json_content, indent=4))
            location = json_location

    if location:
        return Location(**location)

    else:
        raise ValueError(f"Invalid location code: {location_code}")


def all() -> Dict[str, Location]:
    json_locations = Cache.get("locations")

    if not json_locations:
        response = api.request(api_endpoint)
        json_locations = response.json() if response else []
        json_locations = {
            location["location_code"]: location for location in json_locations
        }

        json_content = {
            "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "data": json_locations,
        }

        Cache.cache("locations", json.dumps(json_content, indent=4))

    else:
        json_locations = json.loads(json_locations).get("data")

    locations: Dict[str, Location] = {}

    for code, json_location in json_locations.items():
        locations[code] = Location(*json_location.values())

    return locations
