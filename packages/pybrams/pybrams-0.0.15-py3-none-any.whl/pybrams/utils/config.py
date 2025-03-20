import json
from typing import Any, Dict
from collections import defaultdict
from pathlib import Path


class Config:
    _config = defaultdict(dict)

    @classmethod
    def load_dict_from_file(cls, file_path: Path) -> None:
        if file_path.exists():
            with open(file_path, "r") as f:
                cls.load_dict(json.load(f))
        else:
            print(
                f"Warning: Config file {file_path} not found. Using default configuration."
            )

    @classmethod
    def load_dict(cls, config_dict: Dict[str, Any]) -> None:
        for section, params in config_dict.items():
            if isinstance(params, dict):
                cls._config[section].update(params)
            else:
                cls._config[section] = params

    @classmethod
    def save(cls, file_path: Path | None = None) -> None:
        if file_path is None:
            file_path = Path(__file__).resolve().parents[3] / "config" / "config.json"

        with open(file_path, "w") as f:
            json.dump(cls._config, f, indent=4)

        print(f"Configuration saved to {file_path}")

    @classmethod
    def get(cls, section: str, key: str) -> Any:
        value = cls._config
        for section_key in section.split("."):
            if not isinstance(value, dict) or section_key not in value:
                raise KeyError(f"Section '{section}' or key '{section_key}' not found.")
            value = value[section_key]
        if key not in value:
            raise KeyError(f"Key '{key}' not found in section '{section}'.")
        return value[key]

    @classmethod
    def set(cls, section: str, key: str, value, save_to_disk=True):
        keys = section.split(".")
        config = cls._config

        for section_key in keys[:-1]:
            if section_key not in config or not isinstance(config[section_key], dict):
                config[section_key] = {}
            config = config[section_key]

        config[key] = value

        if save_to_disk:
            cls.save()

    @classmethod
    def __getitem__(cls, section):
        return cls._config[section]

    @classmethod
    def __getattr__(cls, section):
        if section in cls._config:
            return cls._config[section]
        raise AttributeError(f"'Config' object has no attribute '{section}'")
