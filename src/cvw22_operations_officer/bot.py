# Copyright 2025 Niklas Glienke

import logging
from pathlib import Path
from typing import Any

import yaml
from discord.ext import commands

from cvw22_operations_officer.utils.database import Database


class DiscordBot(commands.Bot):
    """A discord bot that coordinates discord tasks, commands, etc.

    The discord bot coordinates discord tasks, commands, events and also the
    bot configuration. Therefore, this class is solely responsible for the
    communication between the discord server and the bot itself.
    """

    def __init__(
        self, config_dir: str | Path, *args: Any, **kwargs: Any
    ) -> None:
        """Initialize the discord bot.

        Args:
            config_dir (str | Path): Path to the configuration directory.
            *args (Any): Any arguments for the parent class
            **kwargs (Any): Any key-word arguments for the parent class

        """
        super().__init__(*args, **kwargs)

        self.CONFIG_DIR = Path(config_dir)
        self.logger = logging.getLogger(f"cvw22_operations_officer.{__name__}")
        self.config: dict = {}
        self.database = Database(self.CONFIG_DIR)

        self.get_config()

    async def on_ready(self) -> None:
        """Log message that the bot is ready."""
        self.logger.info("CVW22 Operations Officer is ready!")

    def get_config(self) -> None:
        """Get the config from the config.yaml file.

        Raises:
            FileNotFoundError: If the config.yaml could not be accessed.
            yaml.YAMLError: If the YAML content is invalid.

        """
        try:
            with open(
                self.CONFIG_DIR / "config.yaml", "r", encoding="UTF-8"
            ) as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.critical(
                "No 'config.yaml' found in the config directory."
            )
            raise
        except yaml.YAMLError as e:
            self.logger.critical(f"Invalid 'config.yaml': {e}.")
            raise
