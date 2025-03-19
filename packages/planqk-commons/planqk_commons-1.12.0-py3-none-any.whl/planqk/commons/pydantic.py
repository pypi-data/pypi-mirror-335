import inspect
from typing import Any, Dict

from pydantic import BaseModel


def dict_to_pydantic(payload: Dict[str, Any], function_signature: inspect.Signature) -> Any:
    parameter = next(iter(function_signature.parameters.values()))
    parameter_type = parameter.annotation

    if issubclass(parameter_type, BaseModel):
        return parameter_type.model_validate(payload)

    raise ValueError(f"Unsupported data model type: {parameter_type}")
