
## Image `reverse-proxy`

This service hosts the reverse proxy for all services, including SSL certificates via Let's Encrypt.
It is based on the `my-webserver` base image and adds the following steps:

- Deploy custom nginx configuration file (from build context)
- Create a `starship.toml` configuration file for the `starship` prompt (from build context)
- Extend this about file by this section
- Set entry command to start nginx in foreground
