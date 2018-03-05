from datetime import datetime, timedelta
import logging

from nameko.extensions import Entrypoint, ProviderCollector, SharedExtension

from . import constants
from . import client


class DockerEventsManager(SharedExtension, ProviderCollector):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.docker = client.get_client(self.container.config.get(constants.CONFIG_KEY, None))

    def start(self):
        self.container.spawn_managed_thread(
            self.run, identifier=self.__class__.__name__
        )

    def run(self):
        delta = timedelta(seconds=2)
        since = datetime.utcnow()
        until = datetime.utcnow() + delta
        while True:
            for event in self.docker.events(since=since, until=until, decode=True):
                print(event)
                self.dispatch_event(event)
            since = until
            until = datetime.utcnow() + delta

    def dispatch_event(self, event):
        for provider in self._providers:
            #if provider.bot_name == bot_name:
            if provider.filter_event(event):
                provider.handle_event(event)


class DockerEventEntrypoint(Entrypoint):
    """See
    https://docker-py.readthedocs.io/en/stable/client.html#docker.client.DockerClient.events

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
    def __getattribute__(self, _type):
        if not _type in _event_types:
            raise AttributeError('Unknown docker event type: %s' % _type)
        entrypoint_class_name = _type.title() + 'DockerEventEntrypoint'
        entrypoint_class = type(entrypoint_class_name, (DockerEventEntrypoint,),{'_type': _type})
        return entrypoint_class.decorator


docker_events = DockerEventsEntrypointFactory()

