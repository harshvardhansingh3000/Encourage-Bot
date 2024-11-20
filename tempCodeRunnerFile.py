import discord
from discord import message
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests
import nacl  #required for voice related features in discord bots
from discord import FFmpegPCMAudio
import discord.opus
import yt_dlp
from magic_profanity import ProfanityFilter
from discord import member
from discord.ext.commands import has_permissions, MissingPermissions

profanity_filter = ProfanityFilter()

#profanity_filter.load_words([token])

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
#the bot will sense messages with prefix !
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)


@client.event  # This event will be called when the bot is ready to be used
async def on_ready():
    await client.change_presence(status=discord.Status.idle,
                                 activity=discord.Activity(
                                     type=discord.ActivityType.listening,
                                     name="to Sidhu Moose Wala"))
    print(f'We have logged in as {client.user}')
    print('--------------------------------------')
    if not discord.opus.is_loaded():
        discord.opus.load_opus('libopus.so.0')


@client.command()
async def hello(ctx):
    await ctx.send('Hello!, I am the Encourage Bot')


@client.command()
async def goodbye(ctx):
    await ctx.send('Goodbye!, I hope you have a good rest of the day')


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    jokeURL = "https://dad-jokes.p.rapidapi.com/random/joke"
    jokeapi = os.getenv('JOKEAPI')
    headers = {
        "x-rapidapi-key": jokeapi,
        "x-rapidapi-host": "dad-jokes.p.rapidapi.com"
    }

    response = requests.get(jokeURL, headers=headers)

    joke_data = response.json()
    print("Raw Response:", joke_data)
    joke_body = joke_data['body'][0]  # Extract the first joke
    setup = joke_body['setup']  # Get the setup part of the joke
    punchline = joke_body['punchline']  # Get the punchline part of the joke
    if channel:  # If the channel is found, send a message
        await channel.send(f'Welcome to the server, {member.mention}!')
        await channel.send(f"Here's a joke for you:\n**{setup}**\n{punchline}")


@client.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')

    if channel:  # If the channel is found, send a message
        await channel.send(f'GoodBye, {member.mention}!')


@client.command(pass_context=True)
async def join(ctx):
    if (ctx.author.voice):  #if user is running this command in a voice channel
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()  #our bot will join voice channel
        source = FFmpegPCMAudio(
            'voice1.mp3', executable='./ffmpeg-7.0.2-amd64-static/ffmpeg')

        player = voice.play(source)
    else:
        await ctx.send(
            "You are not in a voice channel, you must be in a voice channel to run this command!"
        )


@client.command(pass_context=True)
async def leave(ctx):
    if (ctx.voice_client):  #if bot is in a voice channel
        await ctx.guild.voice_client.disconnect(
        )  #bot will leave voice channel
        await ctx.send("I left the voice channel")
    else:
        await ctx.send("I am not in a voice channel")


@client.command(pass_context=True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@client.command(pass_context=True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@client.command(pass_context=True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


@client.command(pass_context=True)
async def play(ctx, url: str):
    # Check if the bot is connected to a voice channel
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send(
                "You need to be in a voice channel to use this command.")
            return

    # Options for yt-dlp to download the audio as mp3 in Replit's file system
    ydl_opts = {
        'format':
        'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location':
        './ffmpeg-7.0.2-amd64-static/ffmpeg',  # Path to ffmpeg
        'outtmpl':
        '/tmp/%(title)s.%(ext)s',  # Save to Replit's /tmp directory
        'quiet':
        True  # Suppress yt-dlp output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info).replace('.webm',
                                                       '.mp3').replace(
                                                           '.m4a', '.mp3')

    # Check if the file was downloaded correctly
    if os.path.isfile(file_path):
        # Play the audio using FFmpeg
        voice = ctx.guild.voice_client
        source = FFmpegPCMAudio(
            file_path, executable='./ffmpeg-7.0.2-amd64-static/ffmpeg')
        voice.play(source)
        await ctx.send(f"Now playing: {info['title']}")
    else:
        await ctx.send("Failed to download the audio.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if profanity_filter.has_profanity(message.content):
        await message.delete()
        await message.channel.send(
            f'{message.author.mention} Dont send that again or else i will ban you'
        )

    await client.process_commands(message)


@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked.')


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to kick members.")


@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned.')


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to ban members.")


@client.command()
@has_permissions(administrator=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} has been unbanned')
            return


@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to unban")


@client.command()
async def embed(ctx):
    embed = discord.Embed(title="Sample Embed",
                          url="https://google.com",
                          description="This is an embed",
                          color=0xDA8359)
    embed.set_author(
        name=ctx.author.display_name,
        url="https://www.linkedin.com/in/harshvardhan-singh-khurmi-ba3299252/",
        icon_url=ctx.author.avatar)
    embed.set_thumbnail(
        url=
        "https://getwallpapers.com/wallpaper/full/d/b/f/858360-free-scenery-images-wallpapers-1920x1080-for-4k-monitor.jpg"
    )
    embed.add_field(name="Labrodor", value="Cute dogs", inline=True)
    embed.set_footer(text="This is a footer")
    await ctx.send(embed=embed)


@client.command()
async def message(ctx, user: discord.Member, *, message=None):
    message = "Welcome to the server!"
    embed = discord.Embed(title=message, color=0xDA8A59)
    await user.send(embed=embed)


#print(os.getenv('TOKEN'))
# Run the bot (make sure you have the TOKEN set in your environment)
token = os.getenv('TOKEN')
if token is None:
    raise ValueError("TOKEN is not set in the environment variables")
client.run(token)
