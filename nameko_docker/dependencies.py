import logging

from nameko.extensions import DependencyProvider

from . import constants
from . import client


class DockerConnectionError(Exception):
    pass


class Docker(DependencyProvider):

    def setup(self):
        self.docker = client.get_client(self.container.config.get(constants.CONFIG_KEY, None))

    def stop(self):
        del self.docker

    def get_dependency(self, worker_ctx):
        # trigger an exception if we can't interact with docker
        try:
            self.docker.info()
        except OSError as e:
            error_message = 'Failed to connect to docker.'
            logging.error(error_message)
            raise DockerConnectionError(error_message) from e
        return self.docker

