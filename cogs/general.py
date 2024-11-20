import discord
from discord.ext import commands
#from .utils import ProfanityFilter
import requests
import os
from magic_profanity import ProfanityFilter
profanity_filter = ProfanityFilter()

class General(commands.Cog):
    def __init__(self, client):
        self.client = client
        # self.profanity_filter = ProfanityFilter()

    @commands.Cog.listener()
    async def on_member_join(self,member):
        
        channel = discord.utils.get(member.guild.text_channels, name='general')
        jokeURL = "https://dad-jokes.p.rapidapi.com/random/joke"
        jokeapi = os.getenv('JOKEAPI')
        headers = {
            "x-rapidapi-key": jokeapi,
            "x-rapidapi-host": "dad-jokes.p.rapidapi.com"
        }

        response = requests.get(jokeURL, headers=headers)

        joke_data = response.json()
        #print("Raw Response:", joke_data)
        joke_body = joke_data['body'][0]  # Extract the first joke
        setup = joke_body['setup']  # Get the setup part of the joke
        punchline = joke_body['punchline']  # Get the punchline part of the joke
        if channel:  # If the channel is found, send a message
            await channel.send(f'Welcome to the server, {member.mention}!')
            await channel.send(f"Here's a joke for you:\n**{setup}**\n{punchline}")
        await channel.send("Use command !help_command to get information about the amazing things you can do using The Encourage Bot!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = discord.utils.get(member.guild.text_channels, name='general')
        if channel:
            await channel.send(f'Goodbye, {member.mention}!')
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        # Check for profanity
        if profanity_filter.has_profanity(message.content):
            await message.delete()
            await message.channel.send(f'{message.author.mention} Please don\'t use that language.')

        # List of word-reaction pairs
        word_reaction_map = {
            "happy": '😊',
            "sad": '😢',
            "thumbs": '👍',
            "love": '❤️',
            "angry": '😡',
            "wow": '😮',
            "laugh": '😂',
            "cool": '😎',
            "fire": '🔥',
            "party": '🎉',
            "clap": '👏',
            "sleep": '😴',
            "scared": '😨',
            "pray": '🙏',
            "smile": '🙂',
            "music": '🎵',
            "money": '💰',
            "food": '🍕',
            "dog": '🐶',
            "cat": '🐱',
            "heart": '💖',
            "star": '⭐',
            "thinking": '🤔',
            "cry": '😭',
            "scream": '😱',
            "peace": '✌️',
            "fist": '✊',
            "victory": '✌️',
            "broken": '💔',
            "light": '💡',
            "gift": '🎁',
            "trophy": '🏆',
            "sun": '☀️',
            "moon": '🌙',
            "rain": '🌧️',
            "snow": '❄️',
            "wind": '💨',
            "coffee": '☕',
            "beer": '🍺',
            "wine": '🍷',
            "tea": '🍵',
            "cake": '🍰',
            "car": '🚗',
            "bicycle": '🚴',
            "airplane": '✈️',
            "rocket": '🚀',
            "house": '🏠',
            "school": '🏫',
            "book": '📚',
            "phone": '📱',
            "camera": '📷',
            "tv": '📺',
            "computer": '💻',
            "robot": '🤖',
            "alien": '👽',
            "ghost": '👻',
            "devil": '😈',
            "angel": '👼',
            "robot": '🤖',
            "skull": '💀',
            "poop": '💩',
            "diamond": '💎',
            "ball": '⚽',
            "basketball": '🏀',
            "football": '🏈',
            "tennis": '🎾',
            "golf": '⛳',
            "medal": '🥇',
            "hourglass": '⏳',
            "bomb": '💣',
            "target": '🎯',
            "question": '❓',
            "exclamation": '❗',
            "check": '✔️',
            "cross": '❌'
        }

        # React to specific words in the message
        for word, emoji in word_reaction_map.items():
            if word in message.content.lower():
                await message.add_reaction(emoji)
    @commands.command(help = "Greets the user")
    async def hello(self, ctx):
        await ctx.send('Hello! I am the Encourage Bot')

    @commands.command(help = "Gives the user a farewell")
    async def goodbye(self, ctx):
        await ctx.send('Goodbye! I hope you have a good rest of the day')

    # @commands.command()
    # async def message(self, ctx, user: discord.Member, *, message=None):
    #     message = message or "Welcome to the server!"
    #     embed = discord.Embed(title=message, color=0xDA8A59)
    #     await user.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        channel = reaction.message.channel
        await channel.send(user.name + " added " + reaction.emoji)

    @commands.Cog.listener()
    async def on_reaction_remove(self,reaction,user):
        channel = reaction.message.channel
        await channel.send(user.name + " removed " + reaction.emoji)
        
async def setup(client):
    await client.add_cog(General(client))