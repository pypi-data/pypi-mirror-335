from typing import Any, Dict, List

from .serverapplication import JupyterDockerExtensionApp


def _jupyter_server_extension_points() -> List[Dict[str, Any]]:
    return [{
        "module": "jupyter_docker",
        "app": JupyterDockerExtensionApp,
    }]
