# tests/test_interactive.py
import pytest
from unittest.mock import MagicMock, AsyncMock
import discord
from discord.ext import commands
from cogs.interactive import InteractiveComponents

@pytest.mark.asyncio
async def test_role_select(bot, ctx):
    # Arrange
    interactive_cog = InteractiveComponents(bot)
    ctx.guild.roles = [
        MagicMock(spec=discord.Role, name="Role1"),
        MagicMock(spec=discord.Role, name="Role2")
    ]
    
    # Create mock interaction
    interaction = MagicMock(spec=discord.Interaction)
    interaction.response.send_message = AsyncMock()
    
    # Act
    role_select = interactive_cog.RoleSelect()
    await role_select.callback(interaction)
    
    # Assert
    interaction.response.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_color_buttons(bot, ctx):
    # Arrange
    interactive_cog = InteractiveComponents(bot)
    
    # Create mock interaction
    interaction = MagicMock(spec=discord.Interaction)
    interaction.response.send_message = AsyncMock()
    
    # Act
    color_buttons = interactive_cog.ColorButtons()
    await color_buttons.red_button.callback(interaction)
    
    # Assert
    interaction.response.send_message.assert_called_once()