import re
import urllib.request
from io import BytesIO

import discord
from discord.ext import commands
from discord.utils import get
from pytube import YouTube

from cogs.MusicManager.ffmpegpcmaudio import FFmpegPCMAudio


class MusicManager(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, args):

        try:
            html = urllib.request.urlopen(
                "https://www.youtube.com/results?search_query=" + '"' + str(args).replace(" ", ''))
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            url = "https://www.youtube.com/watch?v=" + video_ids[0]
            await ctx.channel.send(url)
        except:
            embed = discord.Embed(
                title=" :bangbang: Bot found an error during execution :",
                description=f"Could not find a video with this name.",
                color=0xe74c3c)
            await ctx.send(embed=embed)

        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You are not connected to a voice channel")
            return

        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()

        out = BytesIO()

        video.on_progress = lambda chunk, file_handler, bytes_remaining: self.on_progress(chunk, file_handler,
                                                                                          bytes_remaining)
        out_file = video.stream_to_buffer(out)

        out.seek(0)
        source = FFmpegPCMAudio(out.read(), pipe=True, executable=r"C:\ffmpeg\ffmpeg.exe")
        player = voice.play(source)

    def on_progress(self, chunk: bytes, file_handler: BytesIO, bytes_remaining: int):
        print(bytes_remaining)
        file_handler.write(chunk)



def setup(bot):
    bot.add_cog(MusicManager(bot))
