#! /usr/bin/make

# Paths
SRC_DIR := src
DC := docker compose -f $(SRC_DIR)/docker-compose.yml

# Defaults
ATTACH ?= false
SERVICES ?=

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build    - Build all Docker services"
	@echo "             You can restrict services with SERVICES='service1 service2', also in targets 'up' and 'logs'"
	@echo "  up       - Start all services in detached mode (use ATTACH=true for attached)"
	@echo "  down     - Stop all services"
	@echo "  restart  - Recreate containers"
	@echo "  logs     - Follow logs of all services"
	@echo "  clean    - Remove all containers, images, volumes, networks"
	@echo "  exec     - Run a command in a service: make exec SERVICE=<service> CMD='<command>'"
	@echo "  bash     - Open a bash shell in a service: make bash SERVICE=<service>"

.PHONY: build up down restart logs clean exec bash

build:
	$(DC) build $(SERVICES)

up:
ifeq ($(ATTACH),true)
	$(DC) up $(SERVICES)
else
	$(DC) up -d $(SERVICES)
endif

down:
	$(DC) down

restart: down up

logs:
	$(DC) logs -f $(SERVICES)

clean:
	$(DC) down --rmi all --volumes --remove-orphans

exec:
ifndef SERVICE
	$(error SERVICE is not set. Usage: make exec SERVICE=<service> CMD="<command>")
endif
ifndef CMD
	$(error CMD is not set. Usage: make exec SERVICE=<service> CMD="<command>")
endif
	$(DC) exec $(SERVICE) sh -c "$(CMD)"

bash:
ifndef SERVICE
	$(error SERVICE is not set. Usage: make bash SERVICE=<service>)
endif
	$(DC) exec -it $(SERVICE) bash
