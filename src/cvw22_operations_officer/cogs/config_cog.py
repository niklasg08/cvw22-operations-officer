# Copyright 2025 Niklas Glienke

import json
import logging

from discord.ext import commands

from cvw22_operations_officer.bot import DiscordBot


class ConfigCog(commands.Cog):
    """Handle all config commands"""

    def __init__(self, discord_bot: DiscordBot) -> None:
        """Initialize the discord cog.

        Args:
            discord_bot: The discord bot the cog belongs to.

        """
        self.logger = logging.getLogger(f"cvw22_operations_officer.{__name__}")
        self.bot = discord_bot

    @commands.command()
    async def config(self, ctx: commands.Context, action: str) -> None:
        """Coordinate all config commands.

        Args:
            ctx: The discord context of the command.
            action: The desired action to take.

        """
        if not self.bot.config["commands"]["config"]:
            await ctx.send("The `config` commands have been disabled.")
            return
        elif not self._is_admin(ctx):
            await ctx.send(
                "Permission denied. "
                "The `config` command can only be used by an admin."
            )
            return

        self.logger.info(f"Execute 'config' command with '{action}' action.")

        match action:
            case "update":
                await ctx.send(self._config_update())
            case "show":
                await ctx.send(json.dumps(self.bot.config, indent=4))
            case _:
                await ctx.send("Invalid `config` command.")

    def _config_update(self) -> str:
        """Update the bot config.

        In case of an exception, the user will be notified with the error
        message.

        Returns:
            A str with either the confirmation of the successful update or
            the notification that something went wrong with the error message.

        """
        try:
            self.bot.get_config()
            return "The bot config has been successfully updated."
        except Exception as e:
            return (
                "While updating the bot config, "
                f"the following exception was thrown: `{e}`"
            )

    def _is_admin(self, ctx: commands.Context) -> bool:
        """Check if the context author is an admin.

        Args:
            ctx: The discord context of the command.

        Returns:
            A bool which indicates whether the author is an admin.

        """
        admins: list[int] = []

        for admin in self.bot.config["admins"]:
            admins.append(admin["id"])

        if ctx.author.id in admins:
            return True
        else:
            return False
