# Copyright 2025 Niklas Glienke

from unittest.mock import AsyncMock, MagicMock

import pytest
from discord.channel import TextChannel, VoiceChannel
from freezegun import freeze_time

from cvw22_operations_officer.cogs.brevity_term_cog import BrevityTermCog
from cvw22_operations_officer.models.brevity_term_model import BrevityTerm


@pytest.fixture
def mock_bot():
    bot = MagicMock()

    bot.config = {
        "commands": {"brevity_term": True},
        "tasks": {
            "brevity_term_digest": {
                "enabled": True,
                "time": "12:00",
                "timezone": "UTC",
                "channel_id": 123456789,
            }
        },
    }

    bot.get_channel = MagicMock()
    bot.brevity_term_service = MagicMock()

    return bot


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.send = AsyncMock()
    return ctx


@pytest.mark.asyncio
async def test_brevity_term_enabled_by_config(mock_bot, mock_ctx):
    mock_bot.brevity_term_service.get_brevity_terms_by_term.return_value = [
        BrevityTerm("TERM EQUAL 1", "DESCRIPTION 1")
    ]

    cog = BrevityTermCog(mock_bot)

    await cog.brevity_term(cog, mock_ctx, "TERM EQUAL 1")

    mock_ctx.send.assert_called_once()
    sent_message = mock_ctx.send.call_args.args[0].split("\n")

    assert sent_message[0] == "### Brevity Term: `TERM EQUAL 1`"
    assert sent_message[1] == "> DESCRIPTION 1"


@pytest.mark.asyncio
async def test_brevity_term_disabled_by_config(mock_bot, mock_ctx):
    mock_bot.config["commands"]["brevity_term"] = False

    cog = BrevityTermCog(mock_bot)

    await cog.brevity_term(cog, mock_ctx, "TERM EQUAL 1")

    mock_ctx.send.assert_called_once()
    sent_message = mock_ctx.send.call_args.args[0]

    assert sent_message == "The `brevity_term` command has been disabled."


@pytest.mark.asyncio
async def test_search_brevity_term_single_brevity_terms(mock_bot):
    mock_bot.brevity_term_service.get_brevity_terms_by_term.return_value = [
        BrevityTerm("TERM EQUAL 1", "DESCRIPTION 1")
    ]

    cog = BrevityTermCog(mock_bot)
    output_message = cog._search_brevity_term("TERM EQUAL 1").split("\n")

    assert output_message[0] == "### Brevity Term: `TERM EQUAL 1`"
    assert output_message[1] == "> DESCRIPTION 1"


@pytest.mark.asyncio
async def test_search_brevity_term_multiple_brevity_terms(mock_bot):
    mock_bot.brevity_term_service.get_brevity_terms_by_term.return_value = [
        BrevityTerm("TERM EQUAL 1", "DESCRIPTION 1"),
        BrevityTerm("TERM EQUAL 2", "DESCRIPTION 2 & DESCRIPTION 3"),
        BrevityTerm("TERM EQUAL 3", "DESCRIPTION 4"),
    ]

    cog = BrevityTermCog(mock_bot)
    output_message = cog._search_brevity_term("equal").split("\n")

    assert output_message[0] == "### Brevity Term: `TERM EQUAL 1`"
    assert output_message[1] == "> DESCRIPTION 1"
    assert output_message[2] == "### Brevity Term: `TERM EQUAL 2`"
    assert output_message[3] == "> DESCRIPTION 2"
    assert output_message[4] == "> DESCRIPTION 3"
    assert output_message[5] == "### Brevity Term: `TERM EQUAL 3`"
    assert output_message[6] == "> DESCRIPTION 4"


@pytest.mark.asyncio
async def test_search_brevity_term_nothing_found(mock_bot):
    mock_bot.brevity_term_service.get_brevity_terms_by_term.return_value = []

    cog = BrevityTermCog(mock_bot)
    output_message = cog._search_brevity_term("not equal")

    assert output_message == "No brevity terms found with `not equal`."


@pytest.mark.asyncio
@freeze_time("2025-01-01 12:00:00")
async def test_brevity_term_digest_correct_time(mock_bot):
    mock_channel = AsyncMock(TextChannel)
    mock_bot.get_channel.return_value = mock_channel

    mock_bot.brevity_term_service.get_brevity_term_for_digest.return_value = (
        BrevityTerm("TERM 1", "DESCRIPTION 1")
    )

    cog = BrevityTermCog(mock_bot)

    await cog.brevity_term_digest()

    mock_channel.send.assert_called_once()
    sent_message = mock_channel.send.call_args.args[0].split("\n")

    assert sent_message[0] == "### Brevity Term: `TERM 1`"
    assert sent_message[1] == "> DESCRIPTION 1"


@pytest.mark.asyncio
@freeze_time("2025-01-01 13:33:02")
async def test_brevity_term_digest_wrong_time(mock_bot):
    cog = BrevityTermCog(mock_bot)

    response = await cog.brevity_term_digest()

    assert response is None


@pytest.mark.asyncio
@freeze_time("2025-01-01 12:00:00")
async def test_brevity_term_digest_disabled(mock_bot):
    mock_bot.config["tasks"]["brevity_term_digest"]["enabled"] = False

    cog = BrevityTermCog(mock_bot)

    response = await cog.brevity_term_digest()

    assert response is None


@pytest.mark.asyncio
@freeze_time("2025-01-01 12:00:00")
async def test_brevity_term_digest_channel_not_found(mock_bot):
    mock_bot.get_channel.return_value = None

    cog = BrevityTermCog(mock_bot)

    response = await cog.brevity_term_digest()

    assert response is None


@pytest.mark.asyncio
@freeze_time("2025-01-01 12:00:00")
async def test_brevity_term_digest_wrong_channel_type(mock_bot):
    mock_channel = AsyncMock(VoiceChannel)
    mock_bot.get_channel.return_value = mock_channel

    cog = BrevityTermCog(mock_bot)

    response = await cog.brevity_term_digest()

    assert response is None


def test_format_brevity_term_single_description():
    brevity_term = BrevityTerm("TERM 1", "DESCRIPTION 1")

    formatted_message = BrevityTermCog.format_brevity_term(brevity_term)
    split_message = formatted_message.split("\n")

    assert split_message[0] == "### Brevity Term: `TERM 1`"
    assert split_message[1] == "> DESCRIPTION 1"


def test_format_brevity_term_multiple_description():
    brevity_term = BrevityTerm("TERM 1", "DESCRIPTION 1 & DESCRIPTION 2")

    formatted_message = BrevityTermCog.format_brevity_term(brevity_term)
    split_message = formatted_message.split("\n")

    assert split_message[0] == "### Brevity Term: `TERM 1`"
    assert split_message[1] == "> DESCRIPTION 1"
    assert split_message[2] == "> DESCRIPTION 2"
