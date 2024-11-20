import discord
from discord.ext import commands
import yt_dlp
from discord import FFmpegPCMAudio
import os
import asyncio
import time

class MusicQueue:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def add(self, item):
        await self.queue.put(item)

    async def get(self):
        return await self.queue.get()

    def is_empty(self):
        return self.queue.empty()

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.music_queue = MusicQueue()
        self.current_song = None
        self.start_time = None

    @commands.command(help = "Bot joins the voice channel user is in")
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
            source = FFmpegPCMAudio('voice1.mp3', executable='ffmpeg')
            voice.play(source)
        else:
            await ctx.send("You must be in a voice channel to use this command!")

    @commands.command(help = "Bot leave the voice channel.")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.send("I left the voice channel")
        else:
            await ctx.send("I am not in a voice channel")


    @commands.command(help = "Plays the audio of a youtube url - example - !play url")
    async def play(self, ctx, url: str):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You need to be in a voice channel to use this command.")
                return

        await ctx.send("Downloading audio... This may take a moment.")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info['title']
                
                # Store current song information
                self.current_song = {
                    'title': info['title'],
                    'channel': info.get('channel', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'views': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'url': url
                }

            mp3_filename = os.path.splitext(filename)[0] + '.mp3'

            FFMPEG_OPTIONS = {
                'options': '-vn'
            }

            voice = ctx.voice_client
            source = FFmpegPCMAudio(mp3_filename, **FFMPEG_OPTIONS)
            
            volume = 0.5
            voice.play(discord.PCMVolumeTransformer(source, volume=volume))
            
            # Set start time when song begins playing
            self.start_time = time.time()
            
            await ctx.send(f"Now playing: {title}")

            while voice.is_playing():
                await asyncio.sleep(1)
            os.remove(mp3_filename)
            await ctx.send(f"Finished playing: {title}")
            
            # Clear current song info when finished
            self.current_song = None
            self.start_time = None

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            self.current_song = None
            self.start_time = None
    @commands.command(help = "Sets the volume of the bot in the voice channel - example - !volume num(0-100)")
    async def volume(self, ctx, volume: float):
        #"""Change the player volume"""
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(help = "Pauses the audio being played by the bot")
    async def pause(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Currently no audio is playing.")

    @commands.command(help = "Resumes the audio being played by the bot")
    async def resume(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.send("The audio is not paused.")

    @commands.command(help = "Stops the audio being played by the bot")
    async def stop(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        voice.stop()
    @commands.command(help = "Adds the audio of a youtube url to the queue - example - !add url")
    async def add(self, ctx, url: str):
        """Add a song to the queue with full song information"""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'extract_flat': False,
                'noplaylist': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                song_info = {
                    'url': url,
                    'title': info['title'],
                    'channel': info.get('channel', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'views': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', '')
                }
                
            await self.music_queue.add(song_info)
            await ctx.send(f"Added to queue: {song_info['title']} ({song_info['duration'] // 60}:{song_info['duration'] % 60:02d})")
        
        except Exception as e:
            await ctx.send(f"Error adding song to queue: {str(e)}")

    @commands.command(help = "Plays the audios in the queue")
    async def play_queue(self, ctx):
        """Play all songs in the queue"""
        if self.music_queue.is_empty():
            await ctx.send("The queue is empty.")
            return

        if not ctx.voice_client and ctx.author.voice:
            await ctx.author.voice.channel.connect()
        elif not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command.")
            return

        try:
            while not self.music_queue.is_empty():
                if not ctx.voice_client:
                    break
                
                next_song = await self.music_queue.get()
                await self.play(ctx, next_song['url'])
                
                # Wait until the song is done playing
                while ctx.voice_client and ctx.voice_client.is_playing():
                    await asyncio.sleep(1)
                
            await ctx.send("Queue finished playing.")
            
        except Exception as e:
            await ctx.send(f"Error playing queue: {str(e)}")
            self.current_song = None
            self.start_time = None

    @commands.command(help = "Plays a complete youtube playlist - example - !play_playlist url")
    async def play_playlist(self, ctx, url: str):
        """Add all songs from a playlist to the queue and start playing"""
        try:
            await ctx.send("Processing playlist... This may take a moment.")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'extract_flat': 'in_playlist',
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_dict = ydl.extract_info(url, download=False)
                
                if 'entries' not in playlist_dict:
                    await ctx.send("Could not find any videos in the playlist.")
                    return
                
                # Get detailed info for each video
                for video in playlist_dict['entries']:
                    if video:
                        try:
                            video_url = video.get('url', video.get('webpage_url', None))
                            if video_url:
                                song_info = {
                                    'url': video_url,
                                    'title': video.get('title', 'Unknown'),
                                    'channel': video.get('channel', 'Unknown'),
                                    'duration': video.get('duration', 0),
                                    'views': video.get('view_count', 0),
                                    'thumbnail': video.get('thumbnail', '')
                                }
                                await self.music_queue.add(song_info)
                        except Exception as e:
                            await ctx.send(f"Error adding video {video.get('title', 'Unknown')}: {str(e)}")
                            continue

            total_songs = len(playlist_dict['entries'])
            await ctx.send(f"Added {total_songs} songs to the queue from playlist: {playlist_dict.get('title', 'Unknown')}")
            
            # Start playing if not already playing
            if not ctx.voice_client or not ctx.voice_client.is_playing():
                await self.play_queue(ctx)
                
        except Exception as e:
            await ctx.send(f"Error processing playlist: {str(e)}")

    @commands.command(help = "Displays the current queue")
    async def queue(self, ctx):
        """Display the current queue"""
        if self.music_queue.is_empty():
            await ctx.send("The queue is empty.")
            return

        embed = discord.Embed(title="Music Queue", color=discord.Color.blue())
        
        # Add currently playing song
        if self.current_song:
            embed.add_field(
                name="Now Playing",
                value=f"🎵 {self.current_song['title']} ({self.current_song['duration'] // 60}:{self.current_song['duration'] % 60:02d})",
                inline=False
            )

        # Get queue items without removing them
        queue_items = []
        temp_queue = asyncio.Queue()
        
        while not self.music_queue.is_empty():
            item = await self.music_queue.get()
            queue_items.append(item)
            await temp_queue.put(item)
            
        # Restore queue
        self.music_queue.queue = temp_queue

        # Add queue items to embed
        queue_text = ""
        for i, item in enumerate(queue_items, 1):
            duration = f"{item['duration'] // 60}:{item['duration'] % 60:02d}"
            queue_text += f"{i}. {item['title']} ({duration})\n"
            
            # Split into multiple fields if too long
            if i % 10 == 0 or i == len(queue_items):
                embed.add_field(name=f"Queue {i-9}-{i}", value=queue_text, inline=False)
                queue_text = ""

        await ctx.send(embed=embed)


    @commands.command(help = "Display information about the currently playing song")
    async def song_info(self, ctx):
        
        if not self.current_song:
            await ctx.send("No song is currently playing.")
            return

        embed = discord.Embed(title="Now Playing", color=discord.Color.blue())
        embed.add_field(name="Title", value=self.current_song['title'], inline=False)
        embed.add_field(name="Channel", value=self.current_song['channel'], inline=True)
        embed.add_field(name="Duration", value=f"{self.current_song['duration'] // 60}:{self.current_song['duration'] % 60:02d}", inline=True)
        embed.add_field(name="Views", value=f"{self.current_song['views']:,}", inline=True)
        
        if self.current_song['thumbnail']:
            embed.set_thumbnail(url=self.current_song['thumbnail'])

        await ctx.send(embed=embed)

    @commands.command(help = "Display the current playback progress")
    async def now_playing(self, ctx):
        
        if not self.current_song or not self.start_time:
            await ctx.send("No song is currently playing.")
            return

        total_seconds = self.current_song['duration']
        elapsed_seconds = int(time.time() - self.start_time)

        # Ensure elapsed time doesn't exceed total duration
        elapsed_seconds = min(elapsed_seconds, total_seconds)

        bar_length = 20
        filled_length = int(bar_length * elapsed_seconds / total_seconds)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        await ctx.send(f"Playing: {self.current_song['title']}\n[{bar}] {elapsed_seconds//60}:{elapsed_seconds%60:02d}/{total_seconds//60}:{total_seconds%60:02d}")

async def setup(client):
    await client.add_cog(Music(client))