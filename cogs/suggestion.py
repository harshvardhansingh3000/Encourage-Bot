import discord
from discord.ext import commands
from discord import ui
from typing import Dict, Set
import datetime

class SuggestiveComponents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
        self.suggestions: Dict[int, Dict[str, Set[int]]] = {}  
    class SuggestionView(ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog

        @ui.button(emoji="👍", style=discord.ButtonStyle.grey, custom_id="upvote")
        async def upvote(self, interaction: discord.Interaction, button: ui.Button):
            message_id = interaction.message.id
            user_id = interaction.user.id
            
            if message_id not in self.cog.suggestions:
                self.cog.suggestions[message_id] = {"upvotes": set(), "downvotes": set()}
            
            # Handle vote switching
            if user_id in self.cog.suggestions[message_id]["downvotes"]:
                self.cog.suggestions[message_id]["downvotes"].remove(user_id)
            
            # Toggle upvote
            if user_id in self.cog.suggestions[message_id]["upvotes"]:
                self.cog.suggestions[message_id]["upvotes"].remove(user_id)
            else:
                self.cog.suggestions[message_id]["upvotes"].add(user_id)
            
            # Update embed
            embed = interaction.message.embeds[0]
            upvotes = len(self.cog.suggestions[message_id]["upvotes"])
            downvotes = len(self.cog.suggestions[message_id]["downvotes"])
            
            embed.set_footer(text=f"👍 {upvotes} | 👎 {downvotes}")
            await interaction.response.edit_message(embed=embed)

        @ui.button(emoji="👎", style=discord.ButtonStyle.grey, custom_id="downvote")
        async def downvote(self, interaction: discord.Interaction, button: ui.Button):
            message_id = interaction.message.id
            user_id = interaction.user.id
            
            if message_id not in self.cog.suggestions:
                self.cog.suggestions[message_id] = {"upvotes": set(), "downvotes": set()}
            
            # Handle vote switching
            if user_id in self.cog.suggestions[message_id]["upvotes"]:
                self.cog.suggestions[message_id]["upvotes"].remove(user_id)
            
            # Toggle downvote
            if user_id in self.cog.suggestions[message_id]["downvotes"]:
                self.cog.suggestions[message_id]["downvotes"].remove(user_id)
            else:
                self.cog.suggestions[message_id]["downvotes"].add(user_id)
            
            # Update embed
            embed = interaction.message.embeds[0]
            upvotes = len(self.cog.suggestions[message_id]["upvotes"])
            downvotes = len(self.cog.suggestions[message_id]["downvotes"])
            
            embed.set_footer(text=f"👍 {upvotes} | 👎 {downvotes}")
            await interaction.response.edit_message(embed=embed)

    # Add these commands to the existing commands section
    @commands.group(name="suggest", invoke_without_command=True, help="Create a new suggestion for the server - example - !suggest <suggestion>\nDisplay all active suggestions and their votes - example - !suggest list\nClear all suggestions (Admin only) - example - !suggest clear\nShow how to use the suggestion system - example - !suggest help")
    async def suggestion(self, ctx, *, suggestion: str):
        embed = discord.Embed(
            title="Suggestion",
            description=suggestion,
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.display_avatar.url
        )
        embed.set_footer(text="👍 0 | 👎 0")
        
        view = self.SuggestionView(self)
        message = await ctx.send(embed=embed, view=view)
        self.suggestions[message.id] = {"upvotes": set(), "downvotes": set()}

    @suggestion.command(name="list", help="Display all active suggestions and their votes")
    async def list_suggestions(self, ctx):
        if not self.suggestions:
            await ctx.send("No active suggestions!")
            return
        
        embed = discord.Embed(
            title="Active Suggestions",
            color=discord.Color.blue()
        )
        
        for message_id, votes in self.suggestions.items():
            try:
                channel = ctx.guild.get_channel(ctx.channel.id)
                message = await channel.fetch_message(message_id)
                suggestion_text = message.embeds[0].description
                upvotes = len(votes["upvotes"])
                downvotes = len(votes["downvotes"])
                
                embed.add_field(
                    name=f"ID: {message_id}",
                    value=f"**Suggestion:** {suggestion_text[:100]}{'...' if len(suggestion_text) > 100 else ''}\n"
                        f"**Votes:** 👍 {upvotes} | 👎 {downvotes}",
                    inline=False
                )
            except discord.NotFound:
                del self.suggestions[message_id]
        
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @suggestion.command(name="clear", help="Clear all suggestions (Admin only)")
    async def clear_suggestions(self, ctx):
        self.suggestions.clear()
        await ctx.send("All suggestions have been cleared!")

    @suggestion.command(name="help", help="Show how to use the suggestion system")
    async def suggestion_help(self, ctx):
        embed = discord.Embed(
            title="Suggestion System Help",
            color=discord.Color.blue(),
            description="Complete guide to using the suggestion system"
        )

        embed.add_field(
            name="Create a Suggestion",
            value="```!suggest <your suggestion>```\n"
                "Example: !suggest Add a music channel",
            inline=False
        )

        embed.add_field(
            name="List Suggestions",
            value="```!suggest list```\n"
                "Shows all active suggestions and votes.",
            inline=False
        )

        embed.add_field(
            name="Voting",
            value="• Click 👍 to upvote or 👎 to downvote\n"
                "• One vote per person\n"
                "• Can change your vote anytime",
            inline=False
        )

        if ctx.author.guild_permissions.administrator:
            embed.add_field(
                name="Admin Commands",
                value="```!suggest clear```\n"
                    "Removes all suggestions and votes",
                inline=False
            )

        await ctx.send(embed=embed)

    @suggestion.error
    async def suggestion_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide a suggestion! Example: `!suggest Add a music channel`")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
        else:
            await ctx.send(f"An error occurred: {str(error)}")
        
async def setup(bot):
    await bot.add_cog(SuggestiveComponents(bot))