import config
import discord
from discord.ext import commands
import yt_dlp as youtube_dl

DISCORD_TOKEN = config.DISCORD_TOKEN
YT_API_KEY = config.YT_API_KEY

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f'Joined {channel}')
    else:
        await ctx.send("You're not in a voice channel.")

@bot.command()
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
        
        await ctx.send(f'Playing: {title}')
    

bot.run(DISCORD_TOKEN)