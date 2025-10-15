
## Second base image `my-webserver`

This is the base image for all my web services. It is based on `my-climate` and adds the following steps:

- Install `nginx` and remove the default site
- Install CGI support: `fcgiwrap` and `spawn-fcgi`
- Extend this about file by this section
