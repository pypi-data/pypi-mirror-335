import os
from typing import Dict, Any

import yaml


def read_to_dict(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as file:
        openapi = yaml.safe_load(file)

    return openapi


def write_dict(directory_path: str, openapi: Dict[str, Any], filename: str = "openapi.yaml"):
    file_path = os.path.join(directory_path, filename)
    with open(file_path, "w") as file:
        yaml.dump(openapi, file, sort_keys=False)
