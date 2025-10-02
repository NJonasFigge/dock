
# Docker Cheat Sheet

## Hierarchy of Docker components:

+ `docker container` (instance) runs based on
  + `docker image` (predefined state) is built based on
    + `Dockerfile` (build definition)

`docker_compose.yml` manages so-called "services", which define which containers to build and run, how they interact,
and how they are networked.

## Commands:

```bash
docker ps  # Show running containers
docker compose build  # Rebuilds images
docker compose up / down  # Runs / stops all managed containers
docker exec -it <name> bash  # Run bash in container
```
