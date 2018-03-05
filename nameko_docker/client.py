import docker


def get_client(config=None):
    if config:
        return docker.DockerClient(**config)
    else:
        return docker.from_env()
