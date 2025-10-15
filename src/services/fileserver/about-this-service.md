
## Image `fileserver`

This service serves files from a mounted volume.
It is based on the `my-climate` base image and adds the following steps:

- Install `apache2` and `apache2-utils` to serve files as a WebDAV server (and enable necessary modules)
- Deploy a `.htpasswd` file for basic authentication (from build context)
- Deploy a conf file, overwriting `000-default.conf`, to set up WebDAV with authentication (from build context)
- Add a `ServerName` directive to `apache2.conf` to avoid warnings
- Create a `starship.toml` configuration file for the `starship` prompt (from build context)
- Prepare a directory for the webdav root to be mounted into (and set permissions)
- Also prepare a directory for webdav logging (and set permissions)
- Extend this about file by this section
- Set command to start `apache2` in the foreground
