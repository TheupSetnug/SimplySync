# SimplySync
This is a Discord bot that syncs who is fronting in a system in SimplyPlural to a Discord server.

## Configuration File (config.yaml)

There is a configuration file called `config.yaml.example` that you can use as a template for creating your own configuration file. You can copy this file and rename it to `config.yaml` and then fill in the values.

This file contains various configuration settings for the application:

- `API_TOKEN`: This is the token used for authenticating with the SimplyPlural API.
- `SYSTEM_ID`: This is the unique identifier for the system in SimplyPlural.
- `WEBHOOK_POSTS`: This boolean value determines whether webhook posts are enabled (true) or disabled (false).
- `WEBHOOK_URL`: This is the URL where the webhooks will be sent.
- `STATUS_CHANNEL_ID`: This is the ID of the channel in Discord where status updates are posted.
- `DISCORD_TOKEN`: This is the token used for authenticating with Discord.
- `STATUS_MESSAGE_ID`: This is the ID of the status message in Discord.
- `BLACKLISTED_MEMBER_IDS`: This is a list of member IDs in SimplyPlural that are blacklisted.

Please ensure to keep this file secure and do not share it publicly as it contains sensitive information. It is part of gitignore so it should not be committed to the repository.

Added webhook for discord. Testing