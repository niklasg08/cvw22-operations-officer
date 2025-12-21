# Copyright 2025 Niklas Glienke

from textwrap import dedent

import discord
import pytest
import yaml

from cvw22_operations_officer.bot import DiscordBot

VALID_CONFIG = {
    "test_str": "test_value",
    "test_int": 5,
    "test_list": [{"str": "test", "int": 67}, {"str": "test", "int": 68}],
}

INVALID_CONFIG = dedent("""
    test_key: "test_value",
    test_key2 "test_value
    """)


def test_get_config_valid(tmp_path):
    config_file = tmp_path / "config.yaml"

    with open(config_file, "a") as f:
        yaml.safe_dump(VALID_CONFIG, f)

    discord_bot = DiscordBot(
        tmp_path, intents=discord.Intents.all(), command_prefix="!"
    )
    config = discord_bot.config

    assert isinstance(config, dict)
    assert VALID_CONFIG == config


def test_get_config_no_config_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        DiscordBot(tmp_path, intents=discord.Intents.all(), command_prefix="!")


def test_get_config_invalid_yaml(tmp_path):
    config_file = tmp_path / "config.yaml"

    with open(config_file, "a") as f:
        f.write(INVALID_CONFIG)

    with pytest.raises(yaml.YAMLError):
        discord_bot = DiscordBot(
            tmp_path, intents=discord.Intents.all(), command_prefix="!"
        )
        discord_bot.get_config()
