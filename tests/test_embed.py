# tests/test_embed.py
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import discord
from discord.ext import commands
from cogs.embeds import EmbedCreator
from datetime import datetime

@pytest.mark.asyncio
@patch('discord.utils.utcnow', return_value=datetime(2024, 1, 1, 12, 0, 0))
async def test_server_info(mock_utcnow, bot, ctx):
    # Arrange
    embed_cog = EmbedCreator(bot)
    
    # Mock guild and channel
    ctx.guild = MagicMock(spec=discord.Guild)
    ctx.guild.name = "Test Server"
    ctx.guild.member_count = 100
    ctx.guild.created_at = datetime(2024, 1, 1)
    
    ctx.channel = MagicMock(spec=discord.TextChannel)
    ctx.channel.name = "test-channel"
    
    # Act
    await embed_cog.server_info.callback(embed_cog, ctx)
    
    # Assert
    ctx.send.assert_called_once()
    args, kwargs = ctx.send.call_args
    assert 'embed' in kwargs
    embed = kwargs['embed']
    
    # Print embed fields for debugging
    print("\nEmbed fields:")
    for field in embed.fields:
        print(f"{field.name}: {field.value}")
    
    # Check embed properties
    assert embed.title == "Server Info"
    
    # Check fields rather than description
    field_data = {field.name: field.value for field in embed.fields}
    assert field_data["Server"] == "Test Server"
    assert field_data["Member Count"] == "100"
    assert field_data["Channel"] == "test-channel"
