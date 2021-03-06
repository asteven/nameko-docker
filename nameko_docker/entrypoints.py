from datetime import datetime, timedelta
import logging

from nameko.extensions import Entrypoint, ProviderCollector, SharedExtension

from . import constants
from . import client


log = logging.getLogger('nameko_docker')


class DockerEventsManager(SharedExtension, ProviderCollector):
    """Listen for docker events and dispatch them to entrypoint handlers.

    For information about the python docker clients events see:
    https://docker-py.readthedocs.io/en/stable/client.html#docker.client.DockerClient.events
    """
    def __init__(self):
        super().__init__()

    def setup(self):
        self.docker = client.get_client(self.container.config.get(constants.CONFIG_KEY, None))

    def start(self):
        log.info('Starting {0}'.format(
            self.__class__.__name__
        ))

        # Fake a 'container.running' event for all running containers.
        for container in self.docker.containers.list():
            event = {
                'Type': 'container',
                'Action': 'running',
                'id': container.attrs['Id'],
                'from': container.attrs['Image'],
                'time': container.attrs['Created'],
            }
            self.dispatch_event(event)

        self.container.spawn_managed_thread(
            self.run, identifier=self.__class__.__name__
        )

    def stop(self):
        log.info('Stopping {0}'.format(
            self.__class__.__name__
        ))

    def run(self):
        delta = timedelta(seconds=5)
        since = datetime.utcnow()
        until = datetime.utcnow() + delta
        while True:
            for event in self.docker.events(since=since, until=until, decode=True):
                log.debug(event)
                self.dispatch_event(event)
            since = until
            until = datetime.utcnow() + delta

    def dispatch_event(self, event):
        for provider in self._providers:
            if provider.filter_event(event):
                provider.handle_event(event)


class DockerEventEntrypoint(Entrypoint):
    """Base class for docker event entrypoints.

    For available types and events see:
    See https://docs.docker.com/engine/reference/commandline/events/
    """
    manager = DockerEventsManager()

    _type = None

    def __init__(self, event):
        self.event = event

    def setup(self):
        self.manager.register_provider(self)

    def stop(self):
        self.manager.unregister_provider(self)

    def filter_event(self, event):
        return event.get('Type') == self._type \
            and event.get('Action') == self.event

    def handle_event(self, event):
        args = (event,)
        kwargs = {}
        context_data = {}
        self.container.spawn_worker(
            self, args, kwargs, context_data=context_data
        )


_event_types = tuple('container image plugin volume network daemon service node secret config'.split(' '))
class DockerEventsEntrypointFactory():
    """Factory class that creates event type specific
    DockerEventEntrypoint subclasses.
    """
    def __getattribute__(self, _type):
        if not _type in _event_types:
            raise AttributeError('Unknown docker event type: %s' % _type)
        entrypoint_class_name = _type.title() + 'DockerEventEntrypoint'
        entrypoint_class = type(entrypoint_class_name, (DockerEventEntrypoint,),{'_type': _type})
        return entrypoint_class.decorator


docker_events = DockerEventsEntrypointFactory()

