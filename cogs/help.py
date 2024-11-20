import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name='help_command',
        aliases=['commands', 'cmdhelp'],
        help='Shows all available commands'
    )
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Bot Commands and Features",
            description="Here are all the available commands and features:",
            color=discord.Color.blue()
        )
        
        # Add AI capabilities field first
        embed.add_field(
            name="🤖 AI-Powered Assistant",
            value=(
                "I am an AI-powered bot that:\n"
                "• Uses context to provide relevant responses\n"
                "• Learns from conversations\n"
                "• Provides personalized assistance\n"
                "• Maintains conversation history for better understanding"
            ),
            inline=False
        )
        
        # Get all commands from all cogs
        for cog in self.bot.cogs:
            # Get the cog
            current_cog = self.bot.get_cog(cog)
            # Skip this cog if it has no commands
            if not current_cog.get_commands():
                continue
                
            # Add a field for each cog
            command_list = ""
            for command in current_cog.get_commands():
                if not command.hidden:
                    # Add command name and description
                    command_list += f"**!{command.name}** - {command.help or 'No description available'}\n"
            
            if command_list:  # Only add non-empty cogs
                embed.add_field(
                    name=cog,
                    value=command_list,
                    inline=False
                )
        
        # Add footer with additional info
        embed.set_footer(text="Type !help_command <command_name> for more details about a specific command.")
        
        # Add the "Other Features" field
        embed.add_field(
            name="Other Features",
            value=(
                "I can also:\n"
                "• Tell jokes to lighten the mood\n"
                "• React to your messages with emojis\n"
                "• Filter out profanity\n"
                "• Process natural language\n"
                "• Understand context and intent\n"
                "• And more!"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(
        name='help_specific',
        help='Get detailed help for a specific command'
    )
    async def help_specific(self, ctx, command_name=None):
        """Get detailed information about a specific command."""
        if command_name is None:
            await self.help_command(ctx)
            return
            
        command = self.bot.get_command(command_name)
        if command is None:
            await ctx.send(f"Command '{command_name}' not found.")
            return
            
        embed = discord.Embed(
            title=f"Command: {command.name}",
            description=command.description or "No description available",
            color=discord.Color.blue()
        )
        
        # Add command details
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        embed.add_field(name="Usage", value=f"!{command.name}", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))