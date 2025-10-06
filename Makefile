#! /usr/bin/make


# ---------------------------------------------- CONFIGURABLE VARIABLES ------------------------------------------------

# Variables
DC_BASE := docker compose -f src/base-images/docker-compose.yml
DC_MAIN := docker compose -f src/services/docker-compose.yml

# Defaults
SERVICES ?= $(SERVICE)
BUILD_OPTIONS ?=


# --------------------------------------------------- HELP TARGET ------------------------------------------------------

.PHONY: help

help:
	@echo "Building targets:"
	@echo "  prepare-build-base  - Prepare building base images (also done before calling the build-base target)"
	@echo "  build-base          - Build all base images (which are used in all other images)"
	@echo "                        You can use BUILD_OPTIONS='--no-cache' to build without cache, also in target"
	@echo "                        'build'"
	@echo "  build               - Build all Docker services"
	@echo "                        You can restrict services with SERVICES='service1 service2', also in targets"
	@echo "                        'up', 'logs', 'buildover' and 'restart'"
	@echo "  clean               - Remove all containers, images, volumes, networks"
	@echo "Service management targets:"
	@echo "  up                  - Start all services in detached mode"
	@echo "  down                - Stop all services"
	@echo "  logs                - Follow logs of all services (also check out the 'browse' target below for"
	@echo "						   interactive log browsing)"
	@echo "  exec                - Run a command in a service: make exec SERVICE=<service> CMD='<command>'"
	@echo "  shell               - Open a shell in a service: make shell SERVICE=<service>"
	@echo "  browse              - Open log browser (with shell spawning capabilities) for all running containers"
	@echo "Shortcut targets:"
	@echo "  restart             - Equivalent to 'make down | up'"
	@echo "  vup                 - 'Verbose up': Equivalent to 'make up logs'"
	@echo "  iup                 - 'Interactive up': Equivalent to 'make up browse'"


# ------------------------------------------------ BUILDING TARGETS ----------------------------------------------------

.PHONY: prepare-build-base build-base build clean

auth:
	@if [ ! -e /usr/bin/htpasswd ]; then \
  		sudo apt install apache2-utils; \
	fi
	@if [ ! -e src/base-images/papsite-base/auth/devs.htpasswd ]; then \
		echo "--- USER INTERACTION REQUIRED ---"; \
		echo "Please set Papsite devs password for user 'jonas':"; \
		htpasswd -c src/base-images/papsite-base/auth/devs.htpasswd jonas; \
		echo "Please set Papsite devs password for user 'tim':"; \
		htpasswd src/base-images/papsite-base/auth/devs.htpasswd tim; \
	fi
	@if [ ! -e src/base-images/papsite-base/auth/testers.htpasswd ]; then \
		echo "Please set Papsite testers password for user 'betatester':"; \
		htpasswd -c src/base-images/papsite-base/auth/testers.htpasswd betatester; \
	fi
	@if [ ! -e src/services/fileserver/.htpasswd ]; then \
		echo "Please set fileserver password for user 'jonasundchristine':"; \
		htpasswd -c src/services/fileserver/.htpasswd jonasundchristine; \
	fi

re-auth:
	rm -f src/base-images/papsite-base/auth/devs.htpasswd
	rm -f src/base-images/papsite-base/auth/testers.htpasswd
	rm -f src/services/fileserver/.htpasswd
	$(MAKE) auth

prepare-build-base: auth
	cp src/system-setup/config.fish src/base-images/my-climate/
	cp -r src/starship-utils src/base-images/my-climate/

build-base: prepare-build-base down
	$(DC_BASE) build $(BUILD_OPTIONS) myclimate-base && \
  		$(DC_BASE) build $(BUILD_OPTIONS) mywebserver-base && \
  		$(DC_BASE) build $(BUILD_OPTIONS) papsite-base

build: down
	$(DC_MAIN) build $(BUILD_OPTIONS) $(SERVICES)

clean:
	$(DC_MAIN) down --rmi all --volumes --remove-orphans


# ----------------------------------------- SERVICE MANAGEMENT TARGETS -------------------------------------------------

.PHONY: up down logs exec shell browse

up:
	$(DC_MAIN) up -d $(SERVICES)

down:
	@if [ -n "$$(docker ps -q)" ]; then \
		$(DC_MAIN) down; \
	else \
	  	echo "No running containers."; \
	fi

logs:
	$(DC_MAIN) logs -f $(SERVICES) || true  # || true to avoid error when exiting via Ctrl+C

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


# ------------------------------------------------ SHORTCUT TARGETS ----------------------------------------------------

.PHONY: restart vup iup

restart: down up
vup: up logs  # vup for verbose up
iup: up browse  # iup for interactive up


# ---------------------------------------------- SYSTEM SETUP TARGETS --------------------------------------------------

.PHONY: system-full system-minimal

system-full:
	@echo "Starting full system setup..."
	$(MAKE) -C src/system-setup all
	@echo "Full system setup completed. Please restart your terminal session to apply all changes."

system-minimal:
	@echo "Starting minimal system setup..."
	$(MAKE) -C src/system-setup required
	@echo "Minimal system setup completed. Please restart your terminal session to apply all changes."
