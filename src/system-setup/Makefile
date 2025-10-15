#! /usr/bin/make


# ------------------------------------------- CONFIGURABLE VARIABLES ---------------------------------------------------

# - Set fish installation and usage to true, if not specified otherwise
KEEPBASH ?= false
# - Set starship prompt color hue (0-360), default is blueish
PROMPTHUE ?= 210
# - Set further starship args
STARSHIPARGS = --good-spacers --saturation-bounds .0 .2 --quiet


# ------------------------------------------------- HELP TARGET --------------------------------------------------------

.PHONY: help

help:
	@echo "Main targets:"
	@echo "  all                  - Set up everything"
	@echo "  required             - Set up all functionally required parts (ssh, docker, fstab)"
	@echo "Targets for required parts:"
	@echo "  ssh                  - Install OpenSSH client"
	@echo "  docker               - Install Docker and Docker Compose (if not existing)"
	@echo "  fstab                - Set up /etc/fstab entries for additional drives"
	@echo "Environmental targets:"
	@echo "  cheatsheets          - Copy cheatsheets to the home directory"
	@echo "  python-is-python3    - Ensure that 'python' points to 'python3' (creates symlink if not existing)"
	@echo "User shell targets:"
	@echo "  shell                - Set up the shell (Fish by default or Bash, if KEEPBASH=false)"
	@echo "  tmux                 - Install and configure tmux"
	@echo "Beauty targets:"
	@echo "  starship-toml        - Install starship prompt (if not existing) and generate configuration"
	@echo "  starship-activation  - Activate starship prompt in the chosen shell"
	@echo "(All targets can be prefixed with 'clean-' to remove their effects, if applicable.)"


# -------------------------------------------------- MAIN TARGETS ------------------------------------------------------

.PHONY: all required

all: required tmux cheatsheets shell starship-toml starship-activation python-is-python3
required: ssh docker fstab

clean-all: clean-required clean-tmux clean-cheatsheets clean-shell clean-starship-toml clean-starship-activation \
           clean-python-is-python3
clean-required: clean-ssh clean-docker clean-fstab


# -------------------------------------------- TARGETS FOR REQUIRED PARTS ----------------------------------------------

.PHONY: ssh docker fstab clean-ssh clean-docker clean-fstab

ssh:
	sudo apt install -y openssh-client

clean-ssh:
	sudo apt remove -y openssh-client

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

clean-docker:
	sudo apt remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
	sudo rm -rf /etc/apt/keyrings/docker.gpg
	sudo rm -f /etc/apt/sources.list.d/docker.list
	sudo apt update

fstab:
	mkdir -p /mnt/data/Pazifik_2TB
	mkdir -p /mnt/data/Indik_1TB
	#mkdir -p /mnt/data/Atlantik_1TB
	@echo "UUID=EE141C0C141BD685 /mnt/data/Pazifik_2TB nfts defaults 0 2" >> /etc/fstab
	@echo "UUID=4EBE6557BE65389B /mnt/data/Indik_1TB nfts defaults 0 2" >> /etc/fstab
	#@echo "UUID=... /mnt/data/Atlantik_1TB ext4 defaults 0 2" >> /etc/fstab

clean-fstab:
	sed -i '/Pazifik_2TB/d' /etc/fstab
	sed -i '/Indik_1TB/d' /etc/fstab
	#sed -i '/Atlantik_1TB/d' /etc/fstab
	rm -rf /mnt/data/Pazifik_2TB
	rm -rf /mnt/data/Indik_1TB
	#rm -rf /mnt/data/Atlantik_1TB


# --------------------------------------------- ENVIRONMENTAL TARGETS --------------------------------------------------

.PHONY: cheatsheets python-is-python3 clean-cheatsheets clean-python-is-python3

cheatsheets:
	cp -r ./cheatsheets ~/

clean-cheatsheets:
	rm -rf ~/cheatsheets

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

clean-python-is-python3:
	if [ -e /usr/bin/python ] && [ -L /usr/bin/python ]; then \
		sudo rm /usr/bin/python; \
	else \
		echo "'python' is not a symlink to 'python3', not removing."; \
	fi


# ----------------------------------------------- USER SHELL TARGETS ---------------------------------------------------

.PHONY: shell tmux clean-shell clean-tmux

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

clean-shell:
ifneq ($(KEEPBASH),false)
	sudo apt remove -y fish
	sudo chsh -s /usr/bin/bash
	rm -rf ~/.config/fish
else
	rm -f ~/.bash_aliases
endif

tmux:
	sudo apt update
	sudo apt install tmux
	cp ./.tmux.conf ~/
	cp ./.tmux.help ~/

clean-tmux:
	sudo apt remove -y tmux
	rm -f ~/.tmux.conf
	rm -f ~/.tmux.help


# --------------------------------------------------- BEAUTY TARGETS ---------------------------------------------------

.PHONY: starship-toml starship-activation clean-starship-toml clean-starship-activation

starship-toml: python-is-python3
	@if [ ! -e /usr/local/bin/starship ]; then \
  		curl -sS https://starship.rs/install.sh | sh; \
	fi
	python ../starship-utils/generate_starship_toml.py $(PROMPTHUE) -o ~/.config/starship.toml $(STARSHIPARGS)

clean-starship-toml:
	rm -f ~/.config/starship.toml
	if [ -e /usr/local/bin/starship ]; then \
		sudo rm -f /usr/local/bin/starship; \
	fi

starship-activation:
ifeq ($(KEEPBASH),true)
	echo 'eval "$(starship init bash)"' >> ~/.bashrc
else
	echo 'starship init fish | source' >> ~/.config/fish/config.fish
endif

clean-starship-activation:
ifneq ($(KEEPBASH),true)
	sed -i '/starship init fish | source/d' ~/.config/fish/config.fish
else
	sed -i '/starship init bash/d' ~/.bashrc
endif
