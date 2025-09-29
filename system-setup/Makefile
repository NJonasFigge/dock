#! /usr/bin/make

.PHONY: help

# Set fish installation and usage to true, if not specified otherwise
KEEPBASH ?= false
# Set starship prompt color hue (0-360), default is blueish
PROMPTHUE ?= 210


help:
	@echo "Available targets:"
	@echo "  docker               - Install Docker and Docker Compose (if not existing)"
	@echo "  ssh                  - Install OpenSSH client"
	@echo "  auth                 - Set up authentication files (if not existing)"
	@echo "  reauth               - Recreate authentication files (will remove existing ones)"
	@echo "  tmux                 - Install and configure tmux"
	@echo "  cheatsheets          - Copy cheatsheets to the home directory"
	@echo "  shell                - Set up the shell (Fish by default or Bash, if KEEPBASH=false)"
	@echo "  starship-toml        - Install starship prompt (if not existing) and generate configuration"
	@echo "  starship-activation  - Activate starship prompt in the chosen shell"
	@echo "  all                  - Set up all of the above"
	@echo "  required             - Set up functionally required things (which are ssh, docker and auth)"

.PHONY: all required tmux docker auth reauth tmux cheatsheets shell starship

docker:
	@if [ ! -e /usr/bin/docker ]; then \
		sudo apt install -y ca-certificates curl gnupg; \
		sudo install -m 0755 -d /etc/apt/keyrings; \
		curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg; \
		echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null; \
		sudo apt update; \
		sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; \
		sudo usermod -aG docker $USER; \
		echo "--- IMPORTANT ---"; \
		echo "You need to log out and log back in for the group changes to take effect."; \
		echo "Then you can run 'docker run hello-world' to verify the installation."; \
		echo "-----------------"; \
	else \
		echo "Docker is already installed."; \
	fi


ssh:
	sudo apt install -y openssh-client

auth:
	@if [ ! -e /usr/bin/htpasswd ]; then \
  		sudo apt install apache2-utils; \
	fi
	@if [ ! -e ../src/papsite/auth/devs.htpasswd ]; then \
		echo "--- USER INTERACTION REQUIRED ---"; \
		echo "Please set Papsite-Devs password for user 'jonas':"; \
		htpasswd -c ../src/papsite/auth/devs.htpasswd jonas; \
		echo "Please set Papsite-Devs password for user 'tim':"; \
		htpasswd ../src/papsite/auth/devs.htpasswd tim; \
	fi
	@if [ ! -e ../src/papsite/auth/testers.htpasswd ]; then \
		echo "Please set Papsite-Testers password for user 'betatester':"; \
		htpasswd -c ../src/papsite/auth/testers.htpasswd betatester; \
	fi
	@if [ ! -e ../src/webdav/.htpasswd ]; then \
		echo "Please set WebDAV password for user 'jonasundchristine':"; \
		htpasswd -c ../src/webdav/.htpasswd jonasundchristine; \
	fi

reauth:
	rm -f ../src/papsite/auth/devs.htpasswd
	rm -f ../src/papsite/auth/testers.htpasswd
	rm -f ../src/webdav/auth/.htpasswd
	$(MAKE) auth

tmux:
	sudo apt update
	sudo apt install tmux
	cp ./.tmux.conf ~/
	cp ./.tmux.help ~/

cheatsheets:
	cp -r ./cheatsheets ~/

python-is-python3:
	@if [ ! -e /usr/bin/python3 ]; then \
		sudo apt update; \
		sudo apt install -y python3; \
	else \
		echo "Python is already installed."; \
	fi

	@if [ ! -e /usr/bin/python ]; then \
		sudo ln -s /usr/bin/python3 /usr/bin/python; \
	else \
		echo "'python' already points to 'python3'."; \
	fi

shell:
ifeq ($(KEEPBASH),false)
	sudo apt update
	sudo apt install -y fish
	chsh -s /usr/bin/fish
	mkdir -p ~/.config/fish
	cp ./config.fish ~/.config/fish/
else
	chsh -s /usr/bin/bash
	cp ./.bash_aliases ~/.bash_aliases
endif

starship-toml: python-is-python3
	@if [ ! -e /usr/local/bin/starship ]; then \
  		curl -sS https://starship.rs/install.sh | sh; \
	fi
	python ../utils/generate_starship_toml.py $(PROMPTHUE) -o ~/.config/starship.toml --good-spacers

starship-activation:
ifeq ($(KEEPBASH),true)
	echo 'eval "$(starship init bash)"' >> ~/.bashrc
else
	echo 'starship init fish | source' >> ~/.config/fish/config.fish
endif

all: ssh docker auth tmux cheatsheets shell starship-toml starship-activation

required: ssh docker auth
