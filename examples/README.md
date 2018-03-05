### Run examples

```
nameko run --config ./config.yaml service
```

### Poke it

```
# docker info
curl http://127.0.0.1:8001/info

# create container
curl http://127.0.0.1:8001/start/my-alpine-container

# list containers
curl http://127.0.0.1:8001/list

# stop and remove container
curl http://127.0.0.1:8001/stop/my-alpine-container
```

