import discord
from discord.ext import commands
from discord import ui
import json
import datetime
from cogs.botDBMS import BotDatabase

db=BotDatabase()

class FeedbackModal(ui.Modal, title='Feedback Form'):
    rating = ui.TextInput(
        label='Rating (1-10)',
        placeholder='Enter a number between 1 and 10',
        min_length=1,
        max_length=2,
        required=True
    )
    feedback = ui.TextInput(
        label='Your Feedback',
        style=discord.TextStyle.paragraph,
        placeholder='Tell us what you think...',
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            rating_value = int(self.rating.value)
            if not 1 <= rating_value <= 10:
                raise ValueError()

            success = db.save_feedback(
                user=interaction.user, 
                rating=rating_value, 
                feedback=self.feedback.value
            )

            if success:
                await interaction.response.send_message(
                    f"Thank you for your feedback! Rating: {rating_value}/10", 
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "There was an error saving your feedback. Please try again.", 
                    ephemeral=True
                )

        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid rating between 1 and 10!", 
                ephemeral=True
            )

class FeedbackButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Open Feedback Form", style=discord.ButtonStyle.primary)
    async def feedback_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FeedbackModal())

class BugReportModal(ui.Modal, title='Bug Report'):
    bug_title = ui.TextInput(
        label='Bug Title',
        placeholder='Brief description of the bug',
        required=True
    )
    steps = ui.TextInput(
        label='Steps to Reproduce',
        style=discord.TextStyle.paragraph,
        placeholder='1. Step one\n2. Step two\n3. Step three',
        required=True
    )
    expected = ui.TextInput(
        label='Expected Behavior',
        style=discord.TextStyle.short,
        placeholder='What should happen?',
        required=True
    )
    actual = ui.TextInput(
        label='Actual Behavior',
        style=discord.TextStyle.short,
        placeholder='What actually happened?',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        bug_embed = discord.Embed(
            title=f"🐛 Bug Report: {self.bug_title.value}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        bug_embed.add_field(name="Steps to Reproduce", value=self.steps.value, inline=False)
        bug_embed.add_field(name="Expected Behavior", value=self.expected.value, inline=False)
        bug_embed.add_field(name="Actual Behavior", value=self.actual.value, inline=False)
        bug_embed.set_footer(text=f"Reported by {interaction.user}")
        
        # Send to a specific channel if it exists
        bug_channel = discord.utils.get(interaction.guild.channels, name="bug-reports")
        if bug_channel:
            await bug_channel.send(embed=bug_embed)
            await interaction.response.send_message("Bug report submitted successfully!", ephemeral=True)
        else:
            await interaction.response.send_message(embed=bug_embed)

class BugReportButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Report Bug", style=discord.ButtonStyle.danger)
    async def bug_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BugReportModal())

class SuggestionModal(ui.Modal, title='Suggestion Form'):
    suggestion_title = ui.TextInput(
        label='Suggestion Title',
        placeholder='Brief title for your suggestion',
        required=True
    )
    description = ui.TextInput(
        label='Description',
        style=discord.TextStyle.paragraph,
        placeholder='Describe your suggestion in detail...',
        required=True
    )
    benefit = ui.TextInput(
        label='Benefits',
        style=discord.TextStyle.paragraph,
        placeholder='How will this improve things?',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        suggestion_embed = discord.Embed(
            title=f"💡 Suggestion: {self.suggestion_title.value}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        suggestion_embed.add_field(name="Description", value=self.description.value, inline=False)
        suggestion_embed.add_field(name="Benefits", value=self.benefit.value, inline=False)
        suggestion_embed.set_footer(text=f"Suggested by {interaction.user}")
        
        await interaction.response.send_message(embed=suggestion_embed)
        # Add default reactions for voting
        message = await interaction.original_response()
        await message.add_reaction('👍')
        await message.add_reaction('👎')

class SuggestionButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Make Suggestion", style=discord.ButtonStyle.success)
    async def suggest_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SuggestionModal())

class Modals(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="feedback")
    async def feedback(self, ctx):
        """Opens a feedback form modal"""
        await ctx.send("Please fill out our feedback form:", view=FeedbackButton())

    @commands.command()
    async def bug_report(self, ctx):
        """Opens a bug report modal"""
        await ctx.send("Please fill out the bug report form:", view=BugReportButton())

    @commands.command()
    async def suggestion(self, ctx):
        """Opens a suggestion modal"""
        await ctx.send("Please submit your suggestion:", view=SuggestionButton())

async def setup(client):
    await client.add_cog(Modals(client))