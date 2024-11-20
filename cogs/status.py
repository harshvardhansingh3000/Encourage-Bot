import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime

class StatusManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_list = [
            ("cool beats", discord.ActivityType.listening),
            ("chess", discord.ActivityType.playing),
            ("tutorials", discord.ActivityType.watching),
            ("Coding bot features", discord.ActivityType.competing),
            ("GitHub repositories", discord.ActivityType.watching),
            ("Answering questions", discord.ActivityType.competing),
            ("Debugging code", discord.ActivityType.playing),
            ("new tricks", discord.ActivityType.listening),
            ("Exploring new APIs", discord.ActivityType.playing),
            ("voice chat", discord.ActivityType.listening),
            ("documentation", discord.ActivityType.watching),
            ("Compiling data", discord.ActivityType.competing),
            ("Optimizing performance", discord.ActivityType.playing),
            ("Discussing ideas", discord.ActivityType.watching),
            ("Solving algorithms", discord.ActivityType.competing),
            ("Testing new features", discord.ActivityType.playing),
            ("Tracking bugs", discord.ActivityType.watching),
            ("Chilling music", discord.ActivityType.listening),
            ("Contributing to open-source", discord.ActivityType.playing),
            ("Improving error handling", discord.ActivityType.watching),
            ("meme compilations", discord.ActivityType.watching),
            ("Review pull requests", discord.ActivityType.watching),
            ("Refactoring code", discord.ActivityType.competing),
            ("Running test cases", discord.ActivityType.playing),
            ("Building a project", discord.ActivityType.watching),
            ("Exploring new libraries", discord.ActivityType.listening),
            ("Tuning hyperparameters", discord.ActivityType.competing),
            ("data structures", discord.ActivityType.watching),
            ("Planning world domination", discord.ActivityType.playing),
            ("Syncing databases", discord.ActivityType.watching),
            ("Teaching other bots", discord.ActivityType.listening),
            ("Running simulations", discord.ActivityType.playing),
            ("server health", discord.ActivityType.watching),
            ("write clean code", discord.ActivityType.competing)
        ]
        self.current_status = None
        self.change_status.start()
        self.update_time_based_status.start()

    def cog_unload(self):
        self.change_status.cancel()
        self.update_time_based_status.cancel()
        
    async def set_status(self, status_text, activity_type=None):
        if activity_type is None:
            # For simple status messages, use setActivity without a type
            await self.bot.change_presence(activity=discord.CustomActivity(name=status_text))
        else:
            # For status messages with specific activity types
            activity = discord.Activity(type=activity_type, name=status_text)
            await self.bot.change_presence(activity=activity)

    async def set_temp_status(self, status_text, duration=60):
        # Store the old status before changing
        old_status = self.current_status
        
        # Update current status
        self.current_status = (status_text, None)
        
        # Set the temporary status
        await self.bot.change_presence(activity=discord.CustomActivity(name=status_text))
        
        # Wait for the specified duration
        await asyncio.sleep(duration)
        
        # Check if the current status is still the temporary one
        if self.current_status == (status_text, None):
            # If we have an old status to revert to
            if old_status:
                old_text, old_type = old_status
                self.current_status = old_status
                await self.set_status(old_text, old_type)
            else:
                # If no old status, pick a random one
                status_text, activity_type = random.choice(self.status_list)
                self.current_status = (status_text, activity_type)
                await self.set_status(status_text, activity_type)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith("!hello"):
            await self.set_temp_status(f"Saying hello to {message.author.name}", 30)

    @tasks.loop(minutes=5.0)
    async def change_status(self):
        try:
            # Only change status if not showing time-based status
            if not self.is_showing_time_status:
                status_text, activity_type = random.choice(self.status_list)
                self.current_status = (status_text, activity_type)
                await self.set_status(status_text, activity_type)
                print(f"Status changed to: {status_text} with type {activity_type}")
        except Exception as e:
            print(f"Error in change_status: {e}")

    @change_status.before_loop
    async def before_change_status(self):
        await self.bot.wait_until_ready()
        print("Status change loop is starting")

    @tasks.loop(hours=1.0)
    async def update_time_based_status(self):
        try:
            current_hour = datetime.now().hour
            if 6 <= current_hour < 12:
                status = "Good morning!"
            elif 12 <= current_hour < 18:
                status = "Good afternoon!"
            else:
                status = "Good evening!"
            
            # Set flag and show time-based status
            self.is_showing_time_status = True
            self.current_status = (status, None)
            await self.set_status(status)
            print(f"Time-based status updated to: {status}")
            
            # Wait for 1 minute before returning to regular status rotation
            await asyncio.sleep(60)
            
            # Return to regular status rotation if no temporary status was set
            if self.is_showing_time_status:
                self.is_showing_time_status = False
                status_text, activity_type = random.choice(self.status_list)
                self.current_status = (status_text, activity_type)
                await self.set_status(status_text, activity_type)
                print(f"Returned to regular status: {status_text}")
                
        except Exception as e:
            print(f"Error in time_based_status: {e}")
            self.is_showing_time_status = False

    @update_time_based_status.before_loop
    async def before_update_time_based_status(self):
        await self.bot.wait_until_ready()
        print("Time-based status loop is starting")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.set_temp_status(f"Welcoming {member.name}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.set_temp_status(f"{member.name} left the server")

    @commands.command(help = "Displays the number of members in Bot status")
    async def server_stats(self, ctx):
        guild = ctx.guild
        await self.set_temp_status(f"{guild.member_count} members")
        await ctx.send(f"Current server stats: {guild.member_count} members")

    @commands.command(help = "Displays a random status")
    async def random_status(self, ctx):
        status_text, activity_type = random.choice(self.status_list)
        self.current_status = (status_text, activity_type)
        await self.set_status(status_text, activity_type)
        await ctx.send(f"Changed status to: {status_text}")

async def setup(bot):
    await bot.add_cog(StatusManager(bot))