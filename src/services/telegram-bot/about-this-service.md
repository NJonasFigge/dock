
## Image `telegram-bot`

This service hosts a given Telegram bot.
It is based on the `my-climate` base image and adds the following steps:

- Create a `starship.toml` configuration file for the `starship` prompt (from build context)
- Extend this about file by this section
- Set entrypoint to a script that clones the bot repository and runs it
