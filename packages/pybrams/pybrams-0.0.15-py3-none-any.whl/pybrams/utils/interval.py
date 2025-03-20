from __future__ import annotations
from datetime import datetime
from typing import Union, Optional, Tuple


class InvalidIntervalError(ValueError):
    """Custom exception raised when an interval string is invalid."""


class Interval:
    def __init__(self, start: datetime, end: datetime):
        self.start: datetime = start
        self.end: datetime = end

    @classmethod
    def from_string(cls, interval_str: str) -> Union[Interval, datetime]:
        try:
            if "/" in interval_str:
                start_str, end_str = interval_str.split("/")
                start_datetime = datetime.fromisoformat(f"{start_str}+00:00")
                end_datetime = datetime.fromisoformat(f"{end_str}+00:00")
                return cls(start=start_datetime, end=end_datetime)
            else:
                return datetime.fromisoformat(f"{interval_str}+00:00")

        except ValueError:
            raise InvalidIntervalError(f"Invalid interval string: {interval_str}")

    def to_string(self):
        start_str = self.start.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = self.end.strftime("%Y-%m-%dT%H:%M:%S") if self.end else str()
        return start_str + "/" + end_str

    def __repr__(self) -> str:
        if self.end is None:
            return f"Interval(start={self.start.isoformat()})"
        else:
            return (
                f"Interval(start={self.start.isoformat()}, end={self.end.isoformat()})"
            )
