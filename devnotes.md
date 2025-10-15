
# Devnotes

In this file, I will keep notes on development-related topics, including the current progress and additional ideas.

I'll try to classify todos into musts ❗, shoulds ❕ and coulds ❔.


## Releases

In releaes, I want to replace this file by a `releasenotes.md` file, containing all the new features, fixes and changes that where made since the last release.


## Todos

### Host Machine

(Managed in `src/system-setup/`)

- [x] ❗ Automatically mount external drives (e.g., using `fstab`, maybe something on reboot)
- [ ] ❗ Set up automatic backups (e.g., using `rsync`) → Separate service?
- [ ] ❕ Set up firewall (e.g., using `ufw`)? Or is router enough?
- [ ] ❕ Set up network monitoring (e.g., using `nethogs` or `iftop` per container)


### Base Images

(Managed in `src/base-images/`)

- [ ] ❕ Set up zabbix agent for monitoring
- [ ] ❔ Set up automatic security updates (e.g., using `unattended-upgrades`)


### Services

(Managed in `src/services/`)

#### `reverse-proxy`

- [ ] ❕ Set up automatic SSL certificate renewal (e.g., using `certbot`)
- [ ] ❕ Implement anti-abuse mechanisms (e.g., rate limiting, IP blocking)

#### `papsite-live`, `papsite-stage`, `papsite-devtest`

- [ ] ❕ Generate helpful access report for analysis (e.g., using `goaccess`)
- [ ] ❔ Set up automatic deployment (e.g., using Github webhooks, CGI scripts or similar)

#### `fileserver`

- [ ] (❗) Provide files to be served from a volume

#### `ai-server`, `alpacabot`

- [ ] ❗ Set up Llama model using `ollama`
- [ ] ❗ Set up networking for chatbot access to LLM server

#### `zettelbot`, `schaluppenbot`, `eheboostbot`

- [ ] (❗) Reactivate `make run` in entrypoint script (when old server will be down)


### All my Git repos

- [ ] ❔ Fix all projects to have the following properties:
  - A `README.md` with instructions on
    - Installation & setup
    - How to run
    - Inner workings and options
  - First-level folder structure with `src`, `test`, (`docs`, if applicable)
  - A `Makefile` with a detailed help target, if applicable
  - A `requierements.txt`, if applicable
  - All todos and ideas in a `devnotes.md` file like this one
  - Extra git branches for tagged versions
  - A `releasenotes.md` for each version branch

