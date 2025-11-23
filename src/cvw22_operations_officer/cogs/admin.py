# Copyright 2025 Niklas Glienke

from discord.ext import commands


class Admin(commands.Cog):
    """A discord cog for admin commands

    The discord cog handles all commands starting with '!admin'. Since this cog
    shall only be available for admins of the bot, it executes commands only
    when the command author is an admin.
    """
    def __init__(self, discord_bot):
        """Initialize the discord cog

        Args:
            discord_bot (commands.Bot): The discord bot the cog belongs to.

        """
        self.bot = discord_bot

    @commands.command()
    async def admin(self, ctx, *args: str) -> None:
        """Coordinate all admin commands

        Args:
            ctx (commands.Context): The discord context of the command
            *args (str): Scope and Action of the command

        """
        if not self.bot.config["commands"]["config"]:
            await ctx.send("Any 'admin' commands have been disabled.")
            return
        elif not self._is_admin(ctx):
            await ctx.send("Cannot execute command. Permission denied.")
            return

        self.bot.logger.info(f"Execute 'admin' command with {args=}")

        if len(args) < 2:
            await ctx.send("Invalid command. Usage: `!admin <scope> <action>`")
        scope: str = args[0]
        action: str = args[1]

        match scope:
            case "-c" | "--config":
                await ctx.send(self._admin_config(action))
            case _:
                await ctx.send("Invalid scope. Nothing done.")

    def _admin_config(self, action: str) -> str:
        """Handle all commands with the 'config' scope

        Args:
            action (str): The desired action within the scope

        Returns:
            A feedback message for the user.

        """
        match action:
            case "update":
                self.bot.get_config()
                return "Bot configuration has been updated."
            case "show":
                return self.bot.config
            case _:
                return "Invalid action. Nothing done."

    def _is_admin(self, ctx) -> bool:
        """Check if the context author is an admin

        Args:
            ctx (commands.Context): The discord context of the command

        Returns:
            Whether the author is an admin.

        """
        admins: list = []

        for admin in self.bot.config["admins"]:
            admins.append(admin["id"])

        if ctx.author.id in admins:
            return True
        else:
            return False
