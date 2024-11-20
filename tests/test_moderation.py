# tests/test_moderation.py
import pytest
from unittest.mock import MagicMock, AsyncMock
import discord
from discord.ext import commands
from cogs.moderation import Moderation

@pytest.mark.asyncio
async def test_kick_command(bot, ctx):
    # Arrange
    mod_cog = Moderation(bot)
    member = MagicMock(spec=discord.Member)
    member.kick = AsyncMock()
    
    # Access the command's callback directly
    await mod_cog.kick.callback(mod_cog, ctx, member)
    
    # Assert
    member.kick.assert_called_once()
    ctx.send.assert_called_once_with(f'{member.mention} has been kicked.')

@pytest.mark.asyncio
async def test_ban_command(bot, ctx):
    # Arrange
    mod_cog = Moderation(bot)
    member = MagicMock(spec=discord.Member)
    member.ban = AsyncMock()
    
    # Access the command's callback directly
    await mod_cog.ban.callback(mod_cog, ctx, member)
    
    # Assert
    member.ban.assert_called_once()
    ctx.send.assert_called_once_with(f'{member.mention} has been banned.')