# Copyright 2025 Niklas Glienke

import logging
from datetime import time

from discord import TextChannel
from discord.ext import commands, tasks

from cvw22_operations_officer.bot import DiscordBot

BREVITY_TERM_DIGEST_TIME = time(hour=12, minute=0)


class BrevityTerm(commands.Cog):
    """A discord cog for brevity term commands and tasks.

    The discord cog handles all commands starting with '!brevity_term' and
    a task. The task named 'Brevity Term Digest' teaches all users on the
    discord server a new or known brevity term on a daily basis.
    """

    def __init__(self, discord_bot: DiscordBot):
        """Initialize the discord cog

        Args:
            discord_bot (DiscordBot): The discord bot the cog belongs to.

        """
        self.logger = logging.getLogger(f"cvw22_operations_officer.{__name__}")
        self.bot = discord_bot

        self.brevity_term_digest.start()

    async def cog_load(self) -> None:
        """Start 'Brevity Term Digest' task when cog is loaded."""
        self.brevity_term_digest.start()

    @commands.command()
    async def brevity_term(self, ctx: commands.Context, *args: str) -> None:
        """Coordinate all brevity term commands.

        Args:
            ctx (commands.Context): The discord context of the command.
            *args (str): Action and search term of the command.

        """
        if not self.bot.config["commands"]["brevity_term"]:
            await ctx.send("Any 'brevity_term' commands have been disabled")
            return

        self.logger.info(f"Execute 'brevity_term' command with {args=}")

        if len(args) < 2:
            await ctx.send(
                "Invalid command. "
                "Usage: `!brevity_term <action> <search_term>`"
            )
            return
        action: str = args[0]
        search_term: str = args[1].upper()

        match action:
            case "search":
                await ctx.send(self._search_brevity_term(search_term))
            case _:
                await ctx.send("Invalid action. Nothing done.")

    @tasks.loop(time=BREVITY_TERM_DIGEST_TIME)
    async def brevity_term_digest(self):
        """Sends a brevity term at the specified time.

        The task sends each day at the time specified in the
        'BREVITY_TERM_DIGEST_TIME' constant a new brevity term into a specified
        channel.
        """
        task_config = self.bot.config["tasks"]["brevity_term_digest"]

        if not task_config["enabled"]:
            self.logger.info("'Brevity Term Digest' task is disabled.")
            return

        self.logger.info("Executing 'Brevity Term Digest' task...")

        channel_id = task_config["channel_id"]
        channel = self.bot.get_channel(channel_id)

        if channel is None:
            self.logger.critical("'Brevity Term Digest' channel not found.")
            return
        elif not isinstance(channel, TextChannel):
            self.logger.critical(
                "'Brevity Term Digest' channel is not a text channel."
            )
            return

        response = self.bot.database.get_brevity_terms_for_digest()

        output_message = BrevityTerm.format_brevity_term(response)

        await channel.send(output_message)

    @staticmethod
    def format_brevity_term(brevity_term: tuple) -> str:
        """Format the brevity term for discord.

        Note: The output_message contains markdown because discord supports it.

        Args:
            brevity_term (tuple): The brevity term with a term and description.

        Returns:
            str: The formatted brevity term.

        """
        term: str = brevity_term[0]
        descriptions: str = brevity_term[1]

        output_message = f"### Brevity Term: `{term}`"

        for description in descriptions.split("&"):
            output_message += f"\n> {description.strip()}"

        return output_message

    def _search_brevity_term(self, search_term: str) -> str:
        """Get matching brevity terms by a search term.

        Args:
            search_term (str): The search term to search for brevity terms.

        Returns:
            str: The formatted result of the search.

        """
        response = self.bot.database.get_brevity_term_by_name(search_term)
        output_message = ""

        if response:
            for brevity_term in response:
                output_message += BrevityTerm.format_brevity_term(brevity_term)
                output_message += "\n"
        else:
            output_message = f"No brevity terms found with `{search_term}`"

        return output_message
