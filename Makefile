#! /usr/bin/make

# Paths
DC := docker compose -f src/docker-compose.yml

# Defaults
SERVICES ?= $(SERVICE)

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  context        - Prepare build context by copying required files from system-setup to service directories"
	@echo "  build          - Build all Docker services"
	@echo "                   You can restrict services with SERVICES='service1 service2', also in targets"
	@echo "                   'up', 'logs' and buildover"
	@echo "  buildover      - Build all Docker services without using cache"
	@echo "  up             - Start all services in detached mode"
	@echo "  down           - Stop all services"
	@echo "  restart        - Recreate containers"
	@echo "  logs           - Follow logs of all services"
	@echo "  vup            - 'Verbose up': Start all services and open logs"
	@echo "  clean          - Remove all containers, images, volumes, networks"
	@echo "  exec           - Run a command in a service: make exec SERVICE=<service> CMD='<command>'"
	@echo "  shell          - Open a shell in a service: make shell SERVICE=<service>"
	@echo "  browse         - Open log browser (with shell spawning capabilities) for all running containers"
	@echo "  iup            - 'Interactive up': Start all services and open log browser"

.PHONY: context build up vup down restart logs clean exec shell

context:
	cp system-setup/config.fish src/_base/papsite-base/
	cp -r starship-utils src/_base/my-climate/

build: context down
	$(DC) build $(SERVICES)

buildover: context down
	$(DC) build --no-cache $(SERVICES)

up:
	$(DC) up -d $(SERVICES)

down:
	@if [ -n "$$(docker ps -q)" ]; then \
		$(DC) down; \
	else \
	  	echo "No running containers."; \
	fi

restart: down up

logs:
	$(DC) logs -f $(SERVICES) || true  # || true to avoid error when exiting via Ctrl+C

vup: up logs  # vup for verbose up

clean:
	$(DC) down --rmi all --volumes --remove-orphans

exec: up
ifndef SERVICE
	$(error SERVICE is not set. Usage: make exec SERVICE=<service> CMD="<command>")
endif
ifndef CMD
	$(error CMD is not set. Usage: make exec SERVICE=<service> CMD="<command>")
endif
	$(DC) exec $(SERVICE) sh -c "$(CMD)"

shell: up
ifndef SERVICE
	$(error SERVICE is not set. Usage: make shell SERVICE=<service>)
endif
	@if [ -e /usr/bin/fish ]; then \
		echo "Opening fish shell in service '$(SERVICE)'..."; \
		$(DC) exec -it $(SERVICE) fish; \
	else \
		echo "Opening bash shell in service '$(SERVICE)'..."; \
		$(DC) exec -it $(SERVICE) bash; \
	fi

browse:
	@python browse_containers.py

iup: up browse
