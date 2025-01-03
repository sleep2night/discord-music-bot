# Python Version Compatibility: 3.8 to 3.11
import config
import discord
from discord.ext import commands
import yt_dlp as youtube_dl

DISCORD_TOKEN = config.DISCORD_TOKEN
YT_API_KEY = config.YT_API_KEY

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)
default_volume = 0.5

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(aliases=['connect'])
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f'Joined {channel}')
    else:
        await ctx.send("You're not in a voice channel.")

@bot.command(aliases=['disconnect','quit'])
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('Left the voice channel.')
    else:
        await ctx.send("I am not connected to a voice channel.")

@bot.command()
async def play(ctx, *, search: str = None):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You need to join a voice channel first.")
            return
    if not search:
        await ctx.send("Please provide a song title or URL to play.")
        return 

    # Searching YouTube for the video
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'auto'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search, download=False)
            if 'entries' in info:
                info = info['entries'][0] 
            if 'url' in info:
                url = info['url']
            else:
                # Handle case where URL extraction fails
                await ctx.send("Failed to extract a valid audio URL.")
                return
            title = info.get('title','Unknown Title')
            
        except Exception as e:
            await ctx.send(f'An error has occurred while fetching the song: {e}')
            return
      
        # Play audio
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, options='-vn'))
        voice_client.play(source)
        voice_client.source.volume = default_volume
        await ctx.send(f'Playing: {title}')

@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send('Paused the audio.')
    else:
        await ctx.send('No audio is playing.')

@bot.command()
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send('Resumed the audio.')
    else:
        await ctx.send('Audio is not paused.')

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send('Stopped the audio.')
    else:
        await ctx.send('No audio is playing.')

@bot.command()
async def volume(ctx, vol: int = 50):
    voice_client = ctx.voice_client
    if 0 <= vol <= 100:
        voice_client.source.volume = vol / 100
        await ctx.send(f'Set the volume to {vol}%')
    else:
        await ctx.send('Volume must be between 0 and 100.')

@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send('Skipped the audio.')
    else:
        await ctx.send('No audio is playing.')

@bot.command()
async def help_music(ctx):
    help_msg = """
    **Commands:**
- !join, !connect: Connects the bot to the voice channel you are in.
- !leave, !disconnect, !quit: Disconnects the bot from the voice channel.
- !play [song title or URL]: Plays the audio of the provided song.
- !pause: Pauses the audio.
- !resume: Resumes the audio.
- !stop: Stops the audio.
- !volume [0-100]: Sets the volume of the audio.
- !skip: Skips the current audio.
- !help: Displays this message.
    """
    await ctx.send(help_msg)
    
bot.run(DISCORD_TOKEN)