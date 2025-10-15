
# About this service

## Base image `my-climate`

This is the base image for all my other services. It is based on `python:3.12-slim` and adds the following steps:

- Set timezone to Europe/Berlin
- Install basic packages: `bash`, `curl`, `make`, `nano`
- Install and set up SSH client with `.ssh` keys from build context and predefined `known_hosts`
- Install `git`
- Install and set up `fish` shell with `/root/.config/fish/config.fish` from build context
- Install `starship` prompt and deploy utils for building a `starship.toml` using the following command:
  ```shell
  python starship-utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers
  ```
- Deploy this about file and add an `about` alias to view it from everywhere
