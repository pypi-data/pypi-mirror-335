import os
from typing import Dict, Union, ByteString


def list_directory_files(directory_path: str) -> Dict[str, str]:
    if not os.path.isdir(directory_path):
        raise ValueError(f"Path \"{directory_path}\" must be a directory")

    try:
        files = {}
        for f in os.listdir(directory_path):
            file_path = os.path.join(directory_path, f)
            if os.path.isfile(file_path):
                absolute_path = os.path.abspath(file_path)
                # remove file extension from file name
                f = f.split(".")[0]
                files[f] = absolute_path
        return files
    except FileNotFoundError:
        return {}


def write_str_to_file(directory_path: str, file_name: str, content: str) -> str:
    if not os.path.isdir(directory_path):
        raise ValueError(f"Path \"{directory_path}\" must be a directory")

    file_path = os.path.join(directory_path, file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    return file_path


def write_blob_to_file(directory_path: str, file_name: str, content: Union[bytes, bytearray, ByteString]) -> str:
    if not os.path.isdir(directory_path):
        raise ValueError(f"Path \"{directory_path}\" must be a directory")

    file_path = os.path.join(directory_path, file_name)
    with open(file_path, "wb") as file:
        file.write(content)

    return file_path
