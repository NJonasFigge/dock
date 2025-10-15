
## Image `backup-maker`

This service creates backups of Schaluppe, Fregatte and Schatzinsel data between external hard drives.
It is based on the `my-climate` base image and adds the following steps:

- Create a `starship.toml` configuration file for the `starship` prompt (from build context)
- Install `rsync` for making backups and `cron` for scheduling them
- Deploy a cron job that runs a backup-making script every day at 2am (from build context)
- Extend this about file by this section
- Deploy a `keepalive.sh` script that keeps the container alive, so that the cron jobs can run (plus make it executable and set it as entry command)
