#! /usr/bin/make

# Variables
DC_BASE := docker compose -f src/base-images/docker-compose.yml
DC_MAIN := docker compose -f src/services/docker-compose.yml

# Defaults
SERVICES ?= $(SERVICE)

# Default target
.PHONY: help
help:
	@echo "Hottest targets:"
	@echo "  build               - Build all Docker services"
	@echo "                        You can restrict services with SERVICES='service1 service2', also in targets"
	@echo "                        'up', 'logs', 'buildover' and 'restart'"
	@echo "  up                  - Start all services in detached mode"
	@echo "  down                - Stop all services"
	@echo "  restart             - Stop and start all services"
	@echo "  logs                - Follow logs of all services"
	@echo "  browse              - Open log browser (with shell spawning capabilities) for all running containers"
	@echo "  vup                 - 'Verbose up': Start all services and open logs"
	@echo "  iup                 - 'Interactive up': Start all services and open log browser"
	@echo "  exec                - Run a command in a service: make exec SERVICE=<service> CMD='<command>'"
	@echo "  shell               - Open a shell in a service: make shell SERVICE=<service>"
	@echo ""
	@echo "More targets:"
	@echo "  clean               - Remove all containers, images, volumes, networks"
	@echo "  buildover           - Build all Docker services without using cache"
	@echo "  build-base          - Build all base images (used in all other images)"
	@echo "  buildover-base      - Build all base images without using cache"
	@echo "  prepare-build-base  - Prepare building base images (also done before calling the build-base target)"

.PHONY: prepare-build-base build up vup down restart logs clean exec shell

prepare-build-base:
	cp src/system-setup/config.fish src/base-images/my-climate/
	cp -r src/starship-utils src/base-images/my-climate/

build-base: prepare-build-base down
	$(DC_BASE) build my-climate && \
  		$(DC_BASE) build my-webserver && \
  		$(DC_BASE) build papsite-base

buildover-base: prepare-build-base down
	$(DC_BASE) build --no-cache my-climate && \
  		$(DC_BASE) build --no-cache my-webserver && \
  		$(DC_BASE) build --no-cache papsite-base

build: prepare-build-base down
	$(DC_MAIN) build $(SERVICES)

buildover: prepare-build-base down
	$(DC_MAIN) build --no-cache $(SERVICES)

up:
	$(DC_MAIN) up -d $(SERVICES)

down:
	@if [ -n "$$(docker ps -q)" ]; then \
		$(DC_MAIN) down; \
	else \
	  	echo "No running containers."; \
	fi

restart: down up

logs:
	$(DC_MAIN) logs -f $(SERVICES) || true  # || true to avoid error when exiting via Ctrl+C

vup: up logs  # vup for verbose up

clean:
	$(DC_MAIN) down --rmi all --volumes --remove-orphans

exec: up
ifndef SERVICE
	$(error SERVICE is not set. Usage: make exec SERVICE=<service> CMD="<command>")
endif
ifndef CMD
	$(error CMD is not set. Usage: make exec SERVICE=<service> CMD="<command>")
endif
	$(DC_MAIN) exec $(SERVICE) sh -c "$(CMD)"

shell: up
ifndef SERVICE
	$(error SERVICE is not set. Usage: make shell SERVICE=<service>)
endif
	@if [ -e /usr/bin/fish ]; then \
		echo "Opening fish shell in service '$(SERVICE)'..."; \
		$(DC_MAIN) exec -it $(SERVICE) fish; \
	else \
		echo "Opening bash shell in service '$(SERVICE)'..."; \
		$(DC_MAIN) exec -it $(SERVICE) bash; \
	fi

browse:
	@python browse_containers.py

iup: up browse  # iup for interactive up
