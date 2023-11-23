import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # ipv6 addresses cause issues sometimes
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
        {
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }
    ],
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
    
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

            if 'entries' in data:
                # take the first item from a playlist
                data = data['entries'][0]

            if 'url' in data:
                audio_source = discord.FFmpegPCMAudio(data['url'], **ffmpeg_options, executable="ffmpeg")
                if audio_source:
                    return cls(audio_source, data=data)
                else:
                    raise RuntimeError("Audio source is None")
            else:
                raise RuntimeError("No 'url' found in the data")
        except Exception as e:
            print(f"Exception during extraction: {e}")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.is_playing = False
        self.voice_client = None
        self.voice_channel = None
        self.current_song = None
        self.skip_votes = set()
        self.loop = False

    def check_queue(self):
        if len(self.queue) > 0:
            self.is_playing = True
            self.current_song = self.queue.pop(0)
            self.voice_client.play(self.current_song, after=lambda e: self.play_next_song())
        else:
            self.is_playing = False
    
    def play_next_song(self):
        if self.loop:
            self.queue.append(self.current_song)
        if len(self.queue) > 0:
            self.is_playing = True
            self.current_song = self.queue.pop(0)
            self.voice_client.play(self.current_song, after=lambda e: self.play_next_song())
        else:
            self.is_playing = False
    
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title="Error", description="You must be connected to a voice channel.", color=0xff0000)
            await ctx.send(embed=embed)
            return

        self.voice_channel = ctx.author.voice.channel  # Set the voice channel attribute

        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            await ctx.voice_client.move_to(self.voice_channel)
        else:
            self.voice_client = await self.voice_channel.connect()

    @commands.command()
    async def play(self, ctx, *, url):
        """Plays a song"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            self.queue.append(player)

        embed = discord.Embed(title="Queued", description="Queued: {}".format(player.title), color=0x00ff00)
        await ctx.send(embed=embed)

        if not self.is_playing:
            self.is_playing = True
            self.current_song = self.queue.pop(0)

            # Check if the bot is connected to a voice channel
            if self.voice_client is not None:
                # Check if the voice client is in a valid state
                if self.voice_client.is_connected() and not self.voice_client.is_playing():
                    self.voice_client.play(self.current_song, after=lambda e: self.play_next_song())
                else:
                    # Reconnect to the channel if the client is not in a valid state
                    self.voice_client = await self.voice_channel.connect()
                    self.voice_client.play(self.current_song, after=lambda e: self.play_next_song())
            else:
                # Connect to the channel if the client is None
                self.voice_client = await self.voice_channel.connect()
                self.voice_client.play(self.current_song, after=lambda e: self.play_next_song())
    
    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            embed = discord.Embed(title="Error", description="Not connected to a voice channel.", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        if volume > 100 or volume < 0:
            embed = discord.Embed(title="Error", description="Volume must be between 0 and 100.", color=0xff0000)
            await ctx.send(embed=embed)
            return

        ctx.voice_client.source.volume = volume / 100
        embed = discord.Embed(title="Volume", description="Changed volume to {}%".format(volume), color=0x00ff00)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        self.queue.clear()
        self.is_playing = False
        self.current_song = None
        self.voice_client.stop()

        await ctx.voice_client.disconnect()
        embed = discord.Embed(title="Disconnected", description="I have successfully disconnected from the voice channel.", color=0x00ff00)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def pause(self, ctx):
        """Pauses the current song"""

        ctx.voice_client.pause()
        embed = discord.Embed(title="Paused", description="Paused the current song.", color=0x00ff00)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def resume(self, ctx):
        """Resumes the current song"""

        ctx.voice_client.resume()
        embed = discord.Embed(title="Resumed", description="Resumed the current song.", color=0x00ff00)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip."""

        if ctx.author == self.current_song.requester:
            self.voice_client.stop()
            embed = discord.Embed(title="Skipped", description="Skipped the current song.", color=0x00ff00)
            await ctx.send(embed=embed)
            return
        
        if ctx.author.id not in self.skip_votes:
            self.skip_votes.add(ctx.author.id)
            total_votes = len(self.skip_votes)
            if total_votes >= 3:
                self.voice_client.stop()
                embed = discord.Embed(title="Skipped", description="Skipped the current song.", color=0x00ff00)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Skip", description="Skip vote added, currently at **{}/3**".format(total_votes), color=0x00ff00)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Error", description="You have already voted to skip this song.", color=0xff0000)
            await ctx.send(embed=embed)
    
    @commands.command()
    async def queue(self, ctx):
        """Shows the current queue"""

        if len(self.queue) == 0:
            embed = discord.Embed(title="Error", description="No songs in queue.", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            queue_list = ""
            for i, song in enumerate(self.queue):
                queue_list += "{}. {}\n".format(i+1, song.title)
            embed = discord.Embed(title="Queue", description=queue_list, color=0x00ff00)
            await ctx.send(embed=embed)
    
    @commands.command()
    async def loop(self, ctx):
        """Loops the current song"""

        self.loop = not self.loop
        if self.loop:
            embed = discord.Embed(title="Loop", description="Looping current song", color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Loop", description="Stopped looping current song", color=0x00ff00)
            await ctx.send(embed=embed)
    
    @commands.command()
    async def clear(self, ctx):
        """Clears the queue"""

        self.queue.clear()
        embed = discord.Embed(title="Cleared", description="Cleared the queue", color=0x00ff00)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def remove(self, ctx, index: int):
        """Removes a song from the queue"""

        if index < 1 or index > len(self.queue):
            embed = discord.Embed(title="Error", description="Invalid index", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            self.queue.pop(index-1)
            embed = discord.Embed(title="Removed", description="Removed song at index {}".format(index), color=0x00ff00)
            await ctx.send(embed=embed)
    
    @commands.command()
    async def shuffle(self, ctx):
        """Shuffles the queue"""

        if len(self.queue) == 0:
            embed = discord.Embed(title="Error", description="No songs in queue.", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            import random
            random.shuffle(self.queue)
            embed = discord.Embed(title="Shuffled", description="Shuffled the queue", color=0x00ff00)
            await ctx.send(embed=embed)
    
    @commands.command()
    async def np(self, ctx):
        """Shows the current song"""

        if self.current_song is None:
            embed = discord.Embed(title="Error", description="No song currently playing.", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Now Playing", description=self.current_song.title, color=0x00ff00)
            await ctx.send(embed=embed)
    
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                embed = discord.Embed(title="Error", description="You are not connected to a voice channel.", color=0xff0000)
                await ctx.send(embed=embed)
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


async def setup(bot):
    await bot.add_cog(Music(bot))