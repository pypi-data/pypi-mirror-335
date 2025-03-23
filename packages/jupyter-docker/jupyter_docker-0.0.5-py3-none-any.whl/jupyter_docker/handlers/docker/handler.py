"""Docker handler."""

import json

import docker
import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin

from jupyter_docker._version import __version__


client = docker.from_env()


# pylint: disable=W0223
class ImagesHandler(ExtensionHandlerMixin, APIHandler):
    """The handler to list the docker images."""

    @tornado.web.authenticated
    def get(self):
        """Returns the docker images."""
        images = map(lambda image: image.attrs, client.images.list())
        res = json.dumps({
            "success": True,
            "message": "List of Docker images.",
            "images": list(images),
        }, default=str)
        self.finish(res)


# pylint: disable=W0223
class ContainersHandler(ExtensionHandlerMixin, APIHandler):
    """The handler for docker containers."""

    @tornado.web.authenticated
    def get(self):
        """Returns the docker containers."""
        containers = map(lambda container: container.attrs, client.containers.list())
        res = json.dumps({
            "success": True,
            "message": "List of Docker containers.",
            "containers": list(containers),
        }, default=str)
        self.finish(res)


    @tornado.web.authenticated
    def post(self):
        """Start a container."""
        data = tornado.escape.json_decode(self.request.body)
        image_name = data["imageName"]
        container = client.containers.run(
            image_name,
            stdin_open = True,
            detach = True,
            auto_remove = True,
        )
        res = json.dumps({
            "success": True,
            "message": "Container is started.",
            "container": container.attrs,
        }, default=str)
        self.finish(res)


    @tornado.web.authenticated
    def delete(self, container_id):
        """Delete a container."""
        container = client.containers.get(container_id)
        container.remove(force=True)
        self.set_status(204)
        self.finish()


# pylint: disable=W0223
class VolumesHHandler(ExtensionHandlerMixin, APIHandler):
    """The handler for docker volumes."""

    @tornado.web.authenticated
    def get(self):
        """Returns the docker volumes."""
        volumes = map(lambda volume: volume.attrs, client.volumes.list())
        res = json.dumps({
            "success": True,
            "message": "List of Docker volumes.",
            "volumes": list(volumes),
        }, default=str)
        self.finish(res)


# pylint: disable=W0223
class SecretsHandler(ExtensionHandlerMixin, APIHandler):
    """The handler for docker secrets."""

    @tornado.web.authenticated
    def get(self):
        """Returns the docker secrets."""
        secrets = map(lambda secret: secret.attrs, client.secrets.list())
        res = json.dumps({
            "success": True,
            "message": "List of Docker secrets.",
            "secrets": list(secrets),
        }, default=str)
        self.finish(res)


# pylint: disable=W0223
class NetworksHandler(ExtensionHandlerMixin, APIHandler):
    """The handler for docker networks."""

    @tornado.web.authenticated
    def get(self):
        """Returns the docker secrets."""
        networks = map(lambda network: network.attrs, client.networks.list())
        res = json.dumps({
            "success": True,
            "message": "List of Docker networks.",
            "networks": list(networks),
        }, default=str)
        self.finish(res)
