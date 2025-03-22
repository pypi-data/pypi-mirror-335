import shutil
from pathlib import Path
import os


def copy_scripts():

    print("Copying scripts...")
    destination_dir = Path.cwd() / "pybrams_scripts"
    destination_dir.mkdir(parents=True, exist_ok=True)
    package_dir = os.path.dirname(__file__)
    package_scripts_path = os.path.join(package_dir, "scripts")
    for file_name in os.listdir(package_scripts_path):
        source = os.path.join(package_scripts_path, file_name)
        destination = os.path.join(destination_dir, file_name)
        if os.path.isfile(source):
            shutil.copy(source, destination)

    print(f"Scripts copied to: {destination_dir}")
