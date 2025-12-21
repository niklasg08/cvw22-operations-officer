# Copyright 2025 Niklas Glienke

import datetime
import logging
from zoneinfo import ZoneInfo

from discord import TextChannel
from discord.ext import commands, tasks

from cvw22_operations_officer.bot import DiscordBot
from cvw22_operations_officer.models.brevity_term_model import BrevityTerm


class BrevityTermCog(commands.Cog):
    """Handle all brevity term commands and tasks."""

    def __init__(self, discord_bot: DiscordBot):
        """Initialize the discord cog.

        Args:
            discord_bot: The discord bot the cog belongs to.

        """
        self.logger = logging.getLogger(f"cvw22_operations_officer.{__name__}")
        self.bot = discord_bot

    async def cog_load(self) -> None:  # pragma: no cover
        """Start 'Brevity Term Digest' task when cog is loaded."""
        if self.brevity_term_digest.is_running():
            return

        self.brevity_term_digest.start()

    @commands.command()
    async def brevity_term(
        self, ctx: commands.Context, search_term: str
    ) -> None:
        """Coordinate all brevity term commands.

        Args:
            ctx: The discord context of the command.
            search_term: The term to search for.

        """
        if not self.bot.config["commands"]["brevity_term"]:
            await ctx.send("The 'brevity_term' commands has been disabled.")
            return

        self.logger.info(
            f"Execute 'brevity_term' command with '{search_term}'."
        )

        await ctx.send(self._search_brevity_term(search_term))

    def _search_brevity_term(self, search_term: str) -> str:
        """Get matching brevity terms by a search term.

        Args:
            search_term: The search term to search for.

        Returns:
            The formatted result of the search.

        """
        response = self.bot.brevity_term_service.get_brevity_terms_by_term(
            search_term
        )
        output_message = ""

        if response:
            for brevity_term in response:
                output_message += BrevityTermCog.format_brevity_term(
                    brevity_term
                )
                output_message += "\n"
        else:
            output_message = f"No brevity terms found with `{search_term}`."

        return output_message

    @tasks.loop(minutes=1)
    async def brevity_term_digest(self):
        """Sends a brevity term at the specified time."""
        task_config = self.bot.config["tasks"]["brevity_term_digest"]
        time_zone = ZoneInfo(task_config["timezone"])
        time_now = datetime.datetime.now(time_zone).strftime("%H:%M")

        if not time_now == task_config["time"]:
            return

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

        response = self.bot.brevity_term_service.get_brevity_term_for_digest()

        output_message = BrevityTermCog.format_brevity_term(response)

        await channel.send(output_message)

    @staticmethod
    def format_brevity_term(brevity_term: BrevityTerm) -> str:
        """Format the brevity term for discord.

        Args:
            brevity_term: A brevity term as a BrevityTerm object.

        Returns:
            The formatted brevity term with MARKDOWN syntax as a string.

        """
        output_message = f"### Brevity Term: `{brevity_term.term}`"

        for description in brevity_term.description.split("&"):
            output_message += f"\n> {description.strip()}"

        return output_message
