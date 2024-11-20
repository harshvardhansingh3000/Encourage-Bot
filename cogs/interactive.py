import discord
from discord.ext import commands
from discord import ui
import random
import asyncio
from typing import List, Optional

class InteractiveComponents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    # Role Selection System
    class RoleSelect(ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="Gamer", description="Access to gaming channels", emoji="🎮"),
                discord.SelectOption(label="Artist", description="Access to art channels", emoji="🎨"),
                discord.SelectOption(label="Musician", description="Access to music channels", emoji="🎵"),
                discord.SelectOption(label="Developer", description="Access to coding channels", emoji="💻")
            ]
            super().__init__(
                placeholder="Choose your roles...",
                min_values=0,
                max_values=4,
                options=options,
                custom_id="role_select"
            )

        async def callback(self, interaction: discord.Interaction):
            try:
                # Get the role objects based on selection
                role_names = self.values
                roles = []
                for role_name in role_names:
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if role:
                        roles.append(role)
                
                # Add roles to user
                await interaction.user.add_roles(*roles)
                await interaction.response.send_message(
                    f"Roles updated! Added: {', '.join(role_names)}", 
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "I don't have permission to manage roles!", 
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"An error occurred: {str(e)}", 
                    ephemeral=True
                )

    # Color Selection System
    class ColorButtons(ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        @ui.button(label="Red", style=discord.ButtonStyle.danger, custom_id="red_button")
        async def red_button(self, interaction: discord.Interaction, button: ui.Button):
            try:
                # Try to find and add a red role
                role = discord.utils.get(interaction.guild.roles, name="Red")
                if role:
                    await interaction.user.add_roles(role)
                await interaction.response.send_message("🔴 Red color selected!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

        @ui.button(label="Green", style=discord.ButtonStyle.success, custom_id="green_button")
        async def green_button(self, interaction: discord.Interaction, button: ui.Button):
            try:
                role = discord.utils.get(interaction.guild.roles, name="Green")
                if role:
                    await interaction.user.add_roles(role)
                await interaction.response.send_message("💚 Green color selected!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

        @ui.button(label="Blue", style=discord.ButtonStyle.blurple, custom_id="blue_button")
        async def blue_button(self, interaction: discord.Interaction, button: ui.Button):
            try:
                role = discord.utils.get(interaction.guild.roles, name="Blue")
                if role:
                    await interaction.user.add_roles(role)
                await interaction.response.send_message("💙 Blue color selected!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

    # Mini Game System
    class MiniGame(ui.View):
        def __init__(self):
            super().__init__(timeout=180)  # 3 minute timeout
            self.score = 0
            self.players = {}

        @ui.button(label="Click me!", style=discord.ButtonStyle.primary, custom_id="click_button")
        async def click_counter(self, interaction: discord.Interaction, button: ui.Button):
            player_id = interaction.user.id
            
            if player_id not in self.players:
                self.players[player_id] = 0
            
            self.players[player_id] += 1
            score = self.players[player_id]

            if score >= 10:
                button.disabled = True
                button.label = "Game Over!"
                await interaction.response.edit_message(
                    content=f"{interaction.user.mention} wins with {score} clicks! 🎉",
                    view=self
                )
            else:
                await interaction.response.edit_message(
                    content=f"{interaction.user.mention}'s clicks: {score}",
                    view=self
                )

    # Memory Game System
    class MemoryGame(ui.View):
        def __init__(self):
            super().__init__(timeout=300)  # 5 minute timeout
            self.emojis = ["🎮", "🎨", "🎵", "💻", "🎲", "🎭", "📚", "⚽"]
            self.pairs = self.emojis * 2
            random.shuffle(self.pairs)
            self.buttons = []
            self.create_buttons()
            self.first_pick = None
            self.matches_found = 0
            self.can_pick = True
            self.player = None

        def create_buttons(self):
            for i in range(16):
                button = ui.Button(
                    label="❔",
                    custom_id=f"memory_{i}",
                    row=i//4,
                    style=discord.ButtonStyle.secondary
                )
                button.callback = self.button_callback
                self.buttons.append(button)
                self.add_item(button)

        async def button_callback(self, interaction: discord.Interaction):
            # Set the player on first click
            if not self.player:
                self.player = interaction.user
            
            # Only allow the player who started the game to play
            if interaction.user != self.player:
                await interaction.response.send_message(
                    "This isn't your game! Start your own with !memory",
                    ephemeral=True
                )
                return

            if not self.can_pick:
                await interaction.response.defer()
                return

            button = discord.utils.get(self.buttons, custom_id=interaction.data["custom_id"])
            index = int(button.custom_id.split("_")[1])

            if button.label != "❔":
                await interaction.response.defer()
                return

            if self.first_pick is None:
                self.first_pick = button
                button.label = self.pairs[index]
                button.style = discord.ButtonStyle.primary
                await interaction.response.edit_message(view=self)
            else:
                self.can_pick = False
                button.label = self.pairs[index]
                button.style = discord.ButtonStyle.primary
                await interaction.response.edit_message(view=self)

                if self.pairs[index] == self.pairs[int(self.first_pick.custom_id.split("_")[1])]:
                    self.matches_found += 1
                    button.style = discord.ButtonStyle.success
                    self.first_pick.style = discord.ButtonStyle.success
                    if self.matches_found == 8:
                        for b in self.buttons:
                            b.disabled = True
                        await interaction.followup.send(
                            f"🎉 Congratulations {interaction.user.mention}! You've won!",
                            ephemeral=True
                        )
                else:
                    await asyncio.sleep(1)
                    button.label = "❔"
                    button.style = discord.ButtonStyle.secondary
                    self.first_pick.label = "❔"
                    self.first_pick.style = discord.ButtonStyle.secondary
                    await interaction.message.edit(view=self)

                self.first_pick = None
                self.can_pick = True

    # Commands
    @commands.command(name="menu",help = "Gives role selection menu")
    # @commands.has_permissions(administrator=True)
    async def show_menu(self, ctx):
        """Shows an interactive menu with roles"""
        embed = discord.Embed(
            title="Role Selection Menu",
            description="Select your roles below to access different channels!",
            color=discord.Color.blue()
        )
        view = ui.View(timeout=None)
        view.add_item(self.RoleSelect())
        await ctx.send(embed=embed, view=view)

    @commands.command(name="colors",help = "Gives color selection menu")
    async def color_picker(self, ctx):
        """Shows color picker buttons"""
        embed = discord.Embed(
            title="Color Selection",
            description="Choose your name color:",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=self.ColorButtons())

    @commands.command(name="game",help = "Starts a simple button clicking game")
    async def clicking_game(self, ctx):
        embed = discord.Embed(
            title="Clicking Game",
            description="Click the button 10 times to win!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=self.MiniGame())

    @commands.command(name="memory",help = "Starts a memory matching game")
    async def memory_game(self, ctx):
        embed = discord.Embed(
            title="Memory Game",
            description="Match all the pairs to win!",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed, view=self.MemoryGame())

async def setup(bot):
    await bot.add_cog(InteractiveComponents(bot))