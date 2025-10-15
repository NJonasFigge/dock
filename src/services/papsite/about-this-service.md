
## Image `papsite`

This service hosts `papierschiffdieband.de` (and its subdomains).
It is based on the `papsite-base` base image and adds the following steps:

- Deploy custom nginx configuration file (from build context)
- Run the `add_auth.sh` script to set up basic authentication for staging and devtest instances (from build context)
- Copy the desired CGI scripts from the `build_cgi` directory to the hosted site, then remove the directory
- Create a `starship.toml` configuration file for the `starship` prompt (from build context)
- Extend this about file by this section
- Set entrypoint to the script mentioned in [papsite-base](base-image-papsite-base)
