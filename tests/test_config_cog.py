# Copyright 2025 Niklas Glienke

from unittest.mock import AsyncMock, MagicMock

import pytest

from cvw22_operations_officer.cogs.config_cog import ConfigCog


@pytest.fixture
def mock_bot():
    bot = MagicMock()

    bot.config = {
        "commands": {"config": True},
        "admins": [{"name": "Admin 1", "id": 123456789}],
    }

    bot.get_config = MagicMock()

    return bot


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.send = AsyncMock()
    return ctx


@pytest.mark.asyncio
async def test_config_command_invalid_command(mock_bot, mock_ctx):
    mock_ctx.author.id = 123456789

    cog = ConfigCog(mock_bot)

    await cog.config(cog, mock_ctx, "invalid_action")  # type: ignore

    mock_ctx.send.assert_called_once()
    sent_message = mock_ctx.send.call_args.args[0]

    assert sent_message == "Invalid `config` command."


@pytest.mark.asyncio
async def test_config_command_disabled_by_config(mock_bot, mock_ctx):
    mock_ctx.author.id = 123456789
    mock_bot.config["commands"]["config"] = False

    cog = ConfigCog(mock_bot)

    await cog.config(cog, mock_ctx, "invalid_action")  # type: ignore

    mock_ctx.send.assert_called_once()
    sent_message = mock_ctx.send.call_args.args[0]

    assert sent_message == "The `config` commands have been disabled."


@pytest.mark.asyncio
async def test_config_command_no_admin(mock_bot, mock_ctx):
    mock_ctx.author.id = 000000000

    cog = ConfigCog(mock_bot)

    await cog.config(cog, mock_ctx, "invalid_action")  # type: ignore

    mock_ctx.send.assert_called_once()
    sent_message = mock_ctx.send.call_args.args[0]

    assert sent_message == (
        "Permission denied. The `config` command can only be used by an admin."
    )


@pytest.mark.asyncio
async def test_config_command_show_success(mock_bot, mock_ctx):
    mock_ctx.author.id = 123456789

    cog = ConfigCog(mock_bot)

    await cog.config(cog, mock_ctx, "show")  # type: ignore

    mock_ctx.send.assert_called_once()
    sent_message = mock_ctx.send.call_args.args[0]

    assert (
        sent_message
        == """{
    "commands": {
        "config": true
    },
    "admins": [
        {
            "name": "Admin 1",
            "id": 123456789
        }
    ]
}"""
    )


@pytest.mark.asyncio
async def test_config_command_update_success(mock_bot, mock_ctx):
    mock_ctx.author.id = 123456789

    cog = ConfigCog(mock_bot)

    await cog.config(cog, mock_ctx, "update")  # type: ignore

    mock_ctx.send.assert_called_once()
    sent_message = mock_ctx.send.call_args.args[0]

    assert sent_message == "The bot config has been successfully updated."


def test_config_update_success(mock_bot):
    cog = ConfigCog(mock_bot)

    response = cog._config_update()

    mock_bot.get_config.assert_called_once()

    assert response == "The bot config has been successfully updated."


def test_config_update_exception(mock_bot):
    mock_bot.get_config.side_effect = FileNotFoundError("Test Error.")
    cog = ConfigCog(mock_bot)

    response = cog._config_update()

    assert response == (
        "While updating the bot config, "
        "the following exception was thrown: `Test Error.`"
    )


def test_is_admin_true(mock_bot, mock_ctx):
    mock_ctx.author.id = 123456789

    cog = ConfigCog(mock_bot)

    response = cog._is_admin(mock_ctx)

    assert response


def test_is_admin_false(mock_bot, mock_ctx):
    mock_ctx.author.id = 000000000

    cog = ConfigCog(mock_bot)

    response = cog._is_admin(mock_ctx)

    assert not response
