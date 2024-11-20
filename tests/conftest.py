# tests/conftest.py
import pytest
from unittest.mock import MagicMock, AsyncMock
import discord
from discord.ext import commands

@pytest.fixture
def bot():
    bot = MagicMock(spec=discord.ext.commands.Bot)
    bot.user = MagicMock(spec=discord.User)
    return bot

@pytest.fixture
def ctx():
    ctx = MagicMock(spec=discord.ext.commands.Context)
    ctx.send = AsyncMock()
    ctx.author = MagicMock(spec=discord.Member)
    return ctx