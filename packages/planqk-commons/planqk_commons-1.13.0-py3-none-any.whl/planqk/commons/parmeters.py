import json
from inspect import Signature, Parameter
from typing import Any, Dict, get_origin, get_args, Union, Optional

from pydantic import BaseModel


def files_to_parameters(input_files: Dict[str, str], signature: Signature) -> Dict[str, Any]:
    parameters = {}

    for parameter in signature.parameters.values():
        parameter_name = parameter.name

        if parameter_name not in input_files:
            try:
                parameters[parameter_name] = map_default(parameter)
            except TypeError:
                pass
            continue

        parameters[parameter_name] = map_input_file(input_files[parameter_name], parameter)

    return parameters


def map_input_file(input_file: str, parameter: Parameter):
    parameter_type = parameter.annotation

    origin = get_origin(parameter_type)
    if origin:
        parameter_type = origin

    with open(input_file, "r") as file:
        file_content = file.read()

    return str_to_parameter_type(file_content, parameter_type)


def map_default(parameter: Parameter):
    parameter_type = parameter.annotation

    # use default value if available
    if parameter.default != parameter.empty:
        return parameter.default

    # if optional w/o default, set to None
    elif is_optional_type(parameter_type):
        return None

    # if it is a Pydantic model, try to create an empty instance (using defaults if available)
    elif issubclass(parameter_type, BaseModel):
        return parameter_type.model_validate_json("{}")

    raise TypeError(f"Could not find a default value for parameter '{parameter.name}' of type '{parameter_type}'")


def str_to_parameter_type(data: str, parameter_type: Any) -> Any:
    if issubclass(parameter_type, str):
        return data

    if issubclass(parameter_type, bool):
        return bool(data)

    if issubclass(parameter_type, int):
        return int(data)

    if issubclass(parameter_type, float):
        return float(data)

    if issubclass(parameter_type, (list, dict)):
        return json.loads(data)

    if issubclass(parameter_type, BaseModel):
        return parameter_type.model_validate_json(data)

    raise ValueError(f"Type {parameter_type} is not supported")


def is_simple_type(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool))


def is_container_type(value: Any) -> bool:
    return value is list or value is tuple or value is Union or value is Optional


def is_optional_type(value: Any) -> bool:
    origin = get_origin(value)
    if origin is Union:
        args = get_args(value)
        return len(args) == 2 and type(None) in args
    return origin is Optional
