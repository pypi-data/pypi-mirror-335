from pathlib import Path
import json


class Data:
    _files: dict[Path, str | dict | list] = {}

    @classmethod
    def load(cls, section: str, key: str, from_json=True) -> str | dict | list:
        filepath = (
            Path(__file__).resolve().parents[3]
            / "data"
            / Path(*section.split("."))
            / key
        )

        if filepath in cls._files:
            return cls._files[filepath]

        if not filepath.exists():
            raise FileNotFoundError(f"File not found : {filepath}")

        try:
            with open(filepath, "r") as f:
                data: str | dict | list = json.load(f) if from_json else f.read()
        except PermissionError:
            raise PermissionError(f"Permission denied : {filepath}")

        cls._files[filepath] = data
        return data
