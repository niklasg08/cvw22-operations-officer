# Copyright 2025 Niklas Glienke

import argparse
import asyncio
import logging
import os
import shutil
import sqlite3
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import discord
from dotenv import load_dotenv

from cvw22_operations_officer.bot import DiscordBot
from cvw22_operations_officer.cogs import admin, brevity_term

DEFAULT_CONFIG_DIR = Path(__file__).resolve().parent / "config"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_ROTATION_DAYS = 7
DEFAULT_LOG_BACKUP_COUNT = 1

CONFIG_FILES = ("config.yaml",)


def setup_logging(
    config_dir: str, log_level: str, log_rotate_days: int
) -> logging.Logger:
    """Set up the logging of the discord bot.

    Args:
        config_dir (str): Path to the configuration directory.
        log_level (str): Log level on which the logger minimum logs.
        log_rotate_days (int): Number of days until the log file rotates.

    Returns:
        logging.Logger: The configured logger object.

    """
    log_file = Path(config_dir) / "cvw22_operations_officer.log"

    if log_file.exists():
        log_file.unlink()

    logger = logging.getLogger("cvw22_operations_officer")

    # As specified in the arguments,
    # the log level can only be "INFO" or "DEBUG"
    logger.setLevel(logging.INFO if log_level == "INFO" else logging.DEBUG)

    formatter = logging.Formatter(
        "[%(filename)s:%(lineno)s] %(asctime)s: %(levelname)s: %(message)s"
    )
    handler = TimedRotatingFileHandler(
        log_file,
        when="D",
        interval=log_rotate_days,
        backupCount=DEFAULT_LOG_BACKUP_COUNT,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def setup_config_dir(config_dir: str | Path) -> None:
    """Set up the configuration directory with all required files.

    Args:
        config_dir (str | Path): Path to the configuration directory.

    Raises:
        NotADirectoryError: If the specified configuration directory is not a
            directory.

    """
    # TODO: Improve function if applicable
    config_dir = Path(config_dir)
    config_templates_dir = Path(__file__).resolve().parent / "config_templates"
    database_templates_dir = config_templates_dir / "database"
    database_path = database_templates_dir / "cvw22_operations_officer.db"

    if not config_dir.exists():
        config_dir.mkdir(parents=True)
    elif not config_dir.is_dir():
        raise NotADirectoryError(
            f"Specified Path {config_dir} is not a directory"
        )

    for file in CONFIG_FILES:
        file_path = config_dir / file

        if not file_path.exists():
            shutil.copyfile(config_templates_dir / file, file_path)

    if database_path.exists():
        return

    open(database_path, "a").close()

    with open(database_templates_dir / "schema.sql", "r") as f:
        schema_script = f.read()

    with open(database_templates_dir / "brevity_term.sql", "r") as f:
        brevity_term_script = f.read()

    con = sqlite3.connect(config_dir / "cvw22_operations_officer.db")
    cur = con.cursor()

    cur.executescript(schema_script)
    cur.executescript(brevity_term_script)

    con.commit()
    con.close()


def get_arguments() -> argparse.Namespace:
    """Get parsed arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="""CVW22 Operations Officer:
        Discord Bot for the vCVW22 discord server.""",
    )
    parser.add_argument(
        "-c",
        "--config-dir",
        metavar="path_to_config_dir",
        type=str,
        default=DEFAULT_CONFIG_DIR,
        help="Directory that contains the CVW22 Operations Officer config.",
    )
    parser.add_argument(
        "--log-rotate-days",
        metavar="number_of_days",
        type=int,
        default=DEFAULT_LOG_ROTATION_DAYS,
        help="Specifies number of days for the log rotation.",
    )
    parser.add_argument(
        "--log-level",
        metavar="log_level",
        type=str,
        default=DEFAULT_LOG_LEVEL,
        choices=["DEBUG", "INFO"],
        help="Log level the logger starts to log. Useful for troubleshooting.",
    )

    return parser.parse_args()


async def main() -> None:
    """Set up and run the discord bot."""
    logger = setup_logging(
        args.config_dir,
        args.log_level,
        args.log_rotate_days,
    )
    discord_token = os.getenv("DISCORD_TOKEN")

    if discord_token is None:
        raise RuntimeError("No 'DISCORD_TOKEN' env variable found.")

    intents = discord.Intents.all()
    discord_bot = DiscordBot(
        args.config_dir,
        intents=intents,
        command_prefix="!",
    )

    await discord_bot.add_cog(admin.Admin(discord_bot))
    await discord_bot.add_cog(brevity_term.BrevityTerm(discord_bot))

    logger.info("Starting CVW22 Operations Officer ...")
    await discord_bot.start(discord_token)


if __name__ == "__main__":
    args = get_arguments()
    load_dotenv()
    setup_config_dir(args.config_dir)

    asyncio.run(main())
