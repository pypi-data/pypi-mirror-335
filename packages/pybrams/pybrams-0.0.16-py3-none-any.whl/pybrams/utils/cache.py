import os
import shutil
import glob
from typing import Any, List, Optional, Union, Dict
import logging

logger = logging.getLogger(__name__)

try:
    from typing import Literal

except ImportError:
    from typing_extensions import Literal


class Cache:
    root = os.path.join(".", ".cache")
    use_cache = False
    data = {}

    @classmethod
    def clear(
        cls, metadata_only: bool = False, systems: Optional[List[str]] = None
    ) -> None:
        if metadata_only:
            for file in glob.glob(os.path.join(cls.root, "??????.json")):
                cls.remove(file)

            for file in glob.glob(os.path.join(cls.root, "??????_SYS???.json")):
                cls.remove(file)

            cls.remove(os.path.join(cls.root, "locations.json"))
            cls.remove(os.path.join(cls.root, "systems.json"))

        elif systems:
            for system in systems:
                for file in glob.glob(os.path.join(cls.root, f"{system}*json")):
                    cls.remove(file)

                for file in glob.glob(os.path.join(cls.root, f"*{system}*wav")):
                    cls.remove(file)

        else:
            shutil.rmtree(cls.root, ignore_errors=True)

        cls.data = {}

        logger.info("Clearing cache")

    @classmethod
    def cache(cls, key: str, data: Any, json: bool = True) -> None:
        if cls.use_cache:
            if not os.path.exists(cls.root):
                os.mkdir(cls.root)

            path = f"{key}.json" if json else key
            mode = "w" if json else "wb"

            with open(os.path.join(cls.root, path), mode) as file:
                file.write(data)

            if json:
                cls.data[key] = data

            logger.info(f"Storing {key}")

    @classmethod
    def get(cls, key: str, json: bool = True) -> Union[Any, Literal[False]]:
        if cls.use_cache:
            path = f"{key}.json" if json else key
            mode = "r" if json else "rb"

            if json and key in cls.data:
                return cls.data[key]

            if not os.path.exists(os.path.join(cls.root, path)):
                return False

            with open(os.path.join(cls.root, path), mode) as file:
                data = file.read()
                cls.data[key] = data
                logger.info(f"Retrieving {key}")
                return data

        return False

    @classmethod
    def remove(cls, key: str, json: bool = True) -> bool:
        if cls.use_cache:
            path = f"{key}.json" if json else key
            full_path = os.path.join(cls.root, path)

            if json and key in cls.data:
                del cls.data[key]

            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f"Removed {key}")
                return True

        return False

    @classmethod
    def stats(cls) -> Dict[str, Union[int, float]]:
        if not os.path.exists(cls.root):
            return {
                "number_of_files": 0,
                "total_size_bytes": 0,
                "total_size_kb": 0,
                "total_size_mb": 0,
            }

        total_size = 0
        file_count = 0

        for root, _, files in os.walk(cls.root):
            for file in files:
                file_count += 1
                total_size += os.path.getsize(os.path.join(root, file))

        return {
            "number_of_files": file_count,
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 2),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
