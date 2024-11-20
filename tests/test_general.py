# tests/test_general.py
import pytest
from unittest.mock import MagicMock, AsyncMock, call, ANY
import discord
from discord.ext import commands
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cogs.general import General

@pytest.fixture
def bot():
    bot = MagicMock(spec=discord.ext.commands.Bot)
    bot.user = MagicMock(spec=discord.User)
    return bot

@pytest.fixture
def ctx(bot):
    ctx = MagicMock(spec=discord.ext.commands.Context)
    ctx.send = AsyncMock()
    ctx.author = MagicMock(spec=discord.Member)
    ctx.bot = bot
    return ctx

@pytest.mark.asyncio
async def test_hello_command(bot, ctx):
    # Arrange
    general_cog = General(bot)
    
    # Access the command's callback directly
    await general_cog.hello.callback(general_cog, ctx)
    
    # Assert
    ctx.send.assert_called_once_with('Hello! I am the Encourage Bot')

@pytest.mark.asyncio
async def test_goodbye_command(bot, ctx):
    # Arrange
    general_cog = General(bot)
    
    # Access the command's callback directly
    await general_cog.goodbye.callback(general_cog, ctx)
    
    # Assert
    ctx.send.assert_called_once_with('Goodbye! I hope you have a good rest of the day')

@pytest.mark.asyncio
async def test_on_member_join(bot):
    # Arrange
    general_cog = General(bot)
    member = MagicMock(spec=discord.Member)
    member.mention = '<@123456789>'  # Add explicit mention value
    channel = MagicMock(spec=discord.TextChannel)
    channel.send = AsyncMock()
    member.guild.text_channels = [channel]
    channel.name = 'general'
    
    # Act
    await general_cog.on_member_join(member)
    
    # Assert
    # Check total number of calls
    assert channel.send.call_count == 3
    
    # Check each expected message
    expected_calls = [
        call(f"Welcome to the server, {member.mention}!"),
        call(ANY),  # For the joke message which is random
        call('Use command !help_command to get information about the amazing things you can do using The Encourage Bot!')
    ]
    
    channel.send.assert_has_calls(expected_calls, any_order=True)