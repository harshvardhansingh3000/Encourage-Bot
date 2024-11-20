# tests/test_help.py
import pytest
from unittest.mock import MagicMock, AsyncMock
import discord
from discord.ext import commands
from cogs.help import HelpCommand

@pytest.mark.asyncio
async def test_help_command(bot, ctx):
    # Arrange
    help_cog = HelpCommand(bot)
    
    # Act
    await help_cog.help_command.callback(help_cog, ctx)
    
    # Assert
    ctx.send.assert_called_once()
    # Check if the call contains an embed
    args, kwargs = ctx.send.call_args
    assert 'embed' in kwargs

@pytest.mark.asyncio
async def test_help_specific(bot, ctx):
    # Arrange
    help_cog = HelpCommand(bot)
    command_name = "hello"
    
    # Act
    await help_cog.help_specific.callback(help_cog, ctx, command_name)
    
    # Assert
    ctx.send.assert_called_once()
    args, kwargs = ctx.send.call_args
    assert 'embed' in kwargs