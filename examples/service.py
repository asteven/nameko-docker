import json
import logging
import time

from nameko.web.handlers import http
from nameko.timer import timer
from werkzeug.wrappers import Response

from nameko_docker.dependencies import Docker
from nameko_docker.entrypoints import docker_events


class ExampleService(object):
    name = 'example'
    docker = Docker()


    #@timer(interval=2)
    #def get_count(self):
    #    print('timer: ' + str(self.consul.kv.get('count')))

    @http('GET', '/info')
    def get_info(self, request):
        return Response(
            json.dumps(self.docker.info()),
            mimetype='application/json'
        )

    @http('GET', '/list')
    def get_list(self, request):
        return '\n'.join(['{0.name}: {0.id}'.format(container)
            for container in self.docker.containers.list()])

    @http('GET', '/start/<string:name>')
    def start_alpine(self, request, name):
        container = self.docker.containers.run("alpine", "sleep 300", name=name, detach=True)
        return 'Created: '+ container.id

    @http('GET', '/stop/<string:name>')
    def stop_alpine(self, request, name):
        container = self.docker.containers.get(name)
        container.stop()
        container.remove()
        return 'Stopped: '+ container.id

    @docker_events.container('start')
    def handle_container_start(self, *args, **kwargs):
        print('handle_container_start: %s; %s' % (args, kwargs))

    @docker_events.container('stop')
    def handle_container_stop(self, *args, **kwargs):
        print('handle_container_stop: %s; %s' % (args, kwargs))

    @docker_events.container('die')
    def handle_container_die(self, *args, **kwargs):
        print('handle_container_die: %s; %s' % (args, kwargs))

    @docker_events.container('destroy')
    def handle_container_destroy(self, *args, **kwargs):
        print('handle_container_destroy: %s; %s' % (args, kwargs))

    @docker_events.container('start')
    def handle_container_start(self, *args, **kwargs):
        print('handle_container_start: %s; %s' % (args, kwargs))

    @docker_events.network('connect')
    def handle_network_connect(self, *args, **kwargs):
        print('handle_network_connect: %s; %s' % (args, kwargs))
