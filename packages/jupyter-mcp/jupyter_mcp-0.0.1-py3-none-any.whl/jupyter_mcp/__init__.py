# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

from typing import Any, Dict, List

from .__version__ import __version__
from .serverapplication import JupyterIamExtensionApp


def _jupyter_server_extension_points() -> List[Dict[str, Any]]:
    return [{
        "module": "jupyter_mcp",
        "app": JupyterIamExtensionApp,
    }]
