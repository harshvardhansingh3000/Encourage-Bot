import discord
from discord.ext import commands
import asyncio
import random
import requests
import os

class EmbedCreator(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help="Creates an embed by taking input from users")
    async def create_embed(self, ctx):
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        # Asking user for the embed title
        await ctx.send("Please provide a title for the embed:")
        try:
            title_msg = await self.client.wait_for('message', timeout=60.0, check=check)
            title = title_msg.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            return

        # Asking user for the embed description
        await ctx.send("Please provide a description for the embed:")
        try:
            description_msg = await self.client.wait_for('message', timeout=60.0, check=check)
            description = description_msg.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
            description = None
            
        await ctx.send("Please provide a URL for the embed (or type 'NULL' for no URL):")
        try:
            url_msg = await self.client.wait_for('message', timeout=60.0, check=check)
            url = url_msg.content if url_msg.content.lower() != 'null' else None
        except asyncio.TimeoutError:
            url = None  # If no URL is provided, set to None
        noOfFields = 0
        await ctx.send("Give the number of fields you want to add to the embed")
        try:
            description_msg = await self.client.wait_for('message', timeout=60.0, check=check)
            noOfFields = int(description_msg.content)  # Convert to integer
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond.")
            noOfFields=0
        except ValueError:  # Handle invalid integer conversion
            await ctx.send("That's not a valid number. Please enter an integer.")
            return

        # Create the embed with the provided data
        embed = discord.Embed(title=title, description=description, url=url, color=0xDA8359)
        
        # embed.add_field(name=field_name, value=field_value, inline=True)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)
        embed.set_thumbnail(url="https://getwallpapers.com/wallpaper/full/d/b/f/858360-free-scenery-images-wallpapers-1920x1080-for-4k-monitor.jpg")
        embed.set_footer(text="This embed was created dynamically based on user input")
        for i in range(noOfFields):
            await ctx.send(f"Please provide a field name for field {i + 1}:")
            try:
                field_name_msg = await self.client.wait_for('message', timeout=60.0, check=check)
                field_name = field_name_msg.content
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond. Please try again.")
                return

            # Asking user for the field value
            await ctx.send(f"Please provide a value for the field '{field_name}':")
            try:
                field_value_msg = await self.client.wait_for('message', timeout=60.0, check=check)
                field_value = field_value_msg.content
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond. Please try again.")
                return

            # Add the field to the embed
            embed.add_field(name=field_name, value=field_value, inline=True)
        # Send the embed
        await ctx.send(embed=embed)
        
    @commands.command(help = "Creates an embed giving information about this server")
    async def server_info(self, ctx):
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        embed = discord.Embed(
            title="Server Info",
            description=f"Current time: {current_time}",
            color=0xDA8359
        )

        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar
        )
        
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        embed.add_field(name="Member Count", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="Channel", value=ctx.channel.name, inline=True)
        
        embed.set_footer(text="Data fetched in real-time")

        await ctx.send(embed=embed)

    @commands.command(help = "Creates an embed containing a cute cat image")
    async def random_cat_image(self, ctx):
        # API for random cat picture
        url = "https://random-cat-picture.p.rapidapi.com/meow"
        catapi = os.getenv('JOKEAPI')
        headers = {
            "x-rapidapi-key": catapi, 
            "x-rapidapi-host": "random-cat-picture.p.rapidapi.com"
        }

        # Making the API request
        response = requests.get(url, headers=headers)

        if response.status_code == 200:  # Check if the request was successful
            data = response.json()
            cat_image_url = data.get("file")  # Extract the cat image URL

            # Create a random color
            random_color = random.randint(0, 0xFFFFFF)

            # Create the embed
            embed = discord.Embed(
                title="Random Cat Picture",
                description="Here's a cute cat for you!",
                color=random_color
            )
            embed.set_image(url=cat_image_url)  # Set the cat image in the embed
            embed.set_footer(text="Powered by random-cat-picture API")

            # Send the embed
            await ctx.send(embed=embed)
        else:
            await ctx.send("Sorry, I couldn't fetch a cat picture at the moment.")

async def setup(client):
    await client.add_cog(EmbedCreator(client))
