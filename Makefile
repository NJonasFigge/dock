#! /usr/bin/make

# Paths
DC := docker compose -f src/docker-compose.yml

# Defaults
SERVICES ?= "$SERVICE"

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  prepare-build  - Prepare build by copying necessary config files to service directories"
	@echo "  build          - Build all Docker services"
	@echo "                   You can restrict services with SERVICES='service1 service2', also in targets"
	@echo "                   'up', 'logs' and buildover"
	@echo "  buildover      - Build all Docker services without using cache"
	@echo "  up             - Start all services in detached mode"
	@echo "  up-logs        - Start all services in detached mode and open logs"
	@echo "  down           - Stop all services"
	@echo "  restart        - Recreate containers"
	@echo "  logs           - Follow logs of all services"
	@echo "  clean          - Remove all containers, images, volumes, networks"
	@echo "  exec           - Run a command in a service: make exec SERVICE=<service> CMD='<command>'"
	@echo "  shell          - Open a shell in a service: make shell SERVICE=<service>"

.PHONY: prepare-build build up up-logs down restart logs clean exec shell

prepare-build:
	@for dir in alpaca papsite reverse-proxy telegram-bot webdav; do \
		for file in system-setup/config.fish utils/generate_starship_toml.py utils/starship_template.toml; do \
			rm -f src/$$dir/$$(basename $$file); \
	    	cp $$file src/$$dir/; \
			echo "Added $$(basename $$file) to $$dir."; \
	  	done; \
	done

build: prepare-build down
	$(DC) build $(SERVICES)

buildover: prepare-build down
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
	$(DC) logs -f $(SERVICES)

up-logs: up logs

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

shell:
ifndef SERVICE
	$(error SERVICE is not set. Usage: make bash SERVICE=<service>)
endif
	@if [ -e /usr/bin/fish ]; then \
		echo "Opening fish shell in service '$(SERVICE)'..."; \
		$(DC) exec -it $(SERVICE) fish; \
	else \
		echo "Opening bash shell in service '$(SERVICE)'..."; \
		$(DC) exec -it $(SERVICE) bash; \
	fi
