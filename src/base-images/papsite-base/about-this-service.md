
## Third base image `papsite-base`

This is the base image for all my web services that are part of the public website (papierschiffdieband.de).
It is based on `my-webserver` and adds the following steps:

- Deploy an `auth` directory with basic auth files for `nginx` (from build context)
- Deploy an `add_auth.sh` script to add desired authentication to the nginx config (and make it executable)
- Deploy a `deploy.sh` script that pulls a desired branch of the papsite git repo, makes its `deploy` target and 
copies the result to the webserver root (and make it executable)
- Deploy an `inject_banner.sh` script that injects a banner into all HTML files in the webserver root (and make it executable)
- Deploy a `build_cgi` directory with CGI scripts to be chosen from by derived images (from build context)
- Deploy an `entrypoint.sh` script that calls the `deploy.sh` script on container start and starts nginx (and make it executable)
- Extend this about file by this section
