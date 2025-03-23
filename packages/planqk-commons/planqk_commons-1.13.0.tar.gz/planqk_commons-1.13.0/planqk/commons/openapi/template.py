import os
from enum import Enum
from typing import Dict, Any

from planqk.commons.openapi import resolve_package_path
from planqk.commons.openapi.file import read_to_dict


class OpenApiVersion(Enum):
    V3_0_0 = "3.0.0"
    V3_1_0 = "3.1.0"


def get_template_managed_service(openapi_version: OpenApiVersion = OpenApiVersion.V3_0_0) -> Dict[str, Any]:
    package_path = resolve_package_path()

    if openapi_version == OpenApiVersion.V3_0_0:
        file_path = os.path.join(package_path, "template-managed-service-30.yaml")
    else:
        file_path = os.path.join(package_path, "template-managed-service.yaml")

    openapi = read_to_dict(file_path)

    return openapi
