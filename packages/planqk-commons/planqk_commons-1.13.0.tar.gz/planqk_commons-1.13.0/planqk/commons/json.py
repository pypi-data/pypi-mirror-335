import json
from typing import Optional

from pydantic import BaseModel


def any_to_json(data: any) -> Optional[str]:
    if data is None:
        return None

    if issubclass(data.__class__, BaseModel):
        return data.model_dump_json(indent=2)

    return json.dumps(data, default=lambda o: getattr(o, "__dict__", str(o)), indent=2)
