"""The Jupyter Docker Server application."""

import os

from traitlets import Unicode

from jupyter_server.utils import url_path_join
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin

from jupyter_docker._version import __version__

from .handlers.index.handler import IndexHandler
from .handlers.config.handler import ConfigHandler
from .handlers.docker.handler import (
    ImagesHandler, ContainersHandler, VolumesHHandler,
    SecretsHandler, NetworksHandler,
)
from .handlers.echo.handler import WsEchoHandler
from .handlers.relay.handler import WsRelayHandler
from .handlers.proxy.handler import WsProxyHandler
from .handlers.ping.handler import WsPingHandler


DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./static")

DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "./templates")


class JupyterDockerExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
    """The Jupyter Docker Server extension."""

    name = "jupyter_docker"

    extension_url = "/jupyter_docker"

    load_other_extensions = True

    static_paths = [DEFAULT_STATIC_FILES_PATH]
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]

    config_a = Unicode("", config=True, help="Config A example.")
    config_b = Unicode("", config=True, help="Config B example.")
    config_c = Unicode("", config=True, help="Config C example.")

    def initialize_settings(self):
        pass

    def initialize_templates(self):
        self.serverapp.jinja_template_vars.update({"jupyter_docker_version" : __version__})

    def initialize_handlers(self):
        handlers = [
            ("jupyter_docker", IndexHandler),
            (url_path_join("jupyter_docker", "config"), ConfigHandler),
            #
            (url_path_join("jupyter_docker", "images"), ImagesHandler),
            (url_path_join("jupyter_docker", "containers"), ContainersHandler),
            (r"/jupyter_docker/containers/([^/]+)?", ContainersHandler),
            (url_path_join("jupyter_docker", "volumes"), VolumesHHandler),
            (url_path_join("jupyter_docker", "secrets"), SecretsHandler),
            (url_path_join("jupyter_docker", "networks"), NetworksHandler),
            #
            (url_path_join("jupyter_docker", "echo"), WsEchoHandler),
            (url_path_join("jupyter_docker", "relay"), WsRelayHandler),
            (url_path_join("jupyter_docker", "proxy"), WsProxyHandler),
            (url_path_join("jupyter_docker", "ping"), WsPingHandler),
        ]
        self.handlers.extend(handlers)


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = JupyterDockerExtensionApp.launch_instance
