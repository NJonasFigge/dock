
# Dock

This repo contains the source code for the "Dock", my personal docker compose setup for various services I use.
It's name is derived from the nautical theme of my projects.

## Services

- **reverse-proxy**: A reverse proxy using Nginx to manage and route traffic to various services.
- **papsite-live**: The current live Papierschiff website.
- **papsite-stage**: A staging version of the Papierschiff website for testing changes before going live.
- **papsite-devtest**: A development and testing version of the Papierschiff website.
- **webdav**: A WebDAV server for file storage and sharing.
- **alpaca**: A service for hosting LLMs (Large Language Models).
- **zettelbot**: A Telegram bot for making lists and notes.
- **schaluppenbot**: A Telegram bot for tracking tasks and to-dos inside the folder "Schaluppe".
- **alpacabot**: A Telegram bot for interacting with the Alpaca API.
- **eheboostbot**: A Telegram bot providing tips in relationships.

## Setup Instructions

The following steps outline how to set up and run the services in this repository on a fresh Linux system.

### 1. Prerequisites

#### (If needed:) Install and activate `sudo`

```bash
apt-get update
apt-get install sudo
usermod -aG sudo $USER
```

Log out and log back in to activate the changes.

#### Install `git`

```bash
sudo apt install git
```

#### Install `make`

```bash
sudo apt-get install make
```

Log out and log back in to activate the changes.

### 2. Clone this repository

```bash
git clone https://github.com/NjonasFigge/dock.git 
```

### 3. Set up the rest of your system (to the extend of your liking)

The `system-setup/Makefile` contains various setup steps for your system. To install all of them, run:

```bash
cd dock/system-setup
make all
```

If you only want to run functionally required steps, run:

```bash
make required
```

You can set `KEEPBASH=true` to skip fish shell related steps, if you don't use fish.
