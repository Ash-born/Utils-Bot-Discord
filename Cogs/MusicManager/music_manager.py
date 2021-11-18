from datetime import time

import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
import json
import urllib.request
import re
import youtube_dl
from discord.utils import get
from pytube import YouTube
import os

from main import bot


class MusicManager(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, args):

        try :
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + '"' +str(args).replace(" ",''))
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            url = "https://www.youtube.com/watch?v=" + video_ids[0]
            print(html.read().decode())
            await ctx.channel.send(url)
        except :
                embed = discord.Embed(
                    title=" :bangbang: Bot found an error during execution :",
                    description=f"Could not find a video with this name.",
                    color=0xe74c3c)
                await ctx.send(embed=embed)
        yt = YouTube(url)

        video = yt.streams.filter(only_audio=True).first()

        out_file = video.download(output_path=".")

        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You are not connected to a voice channel")
            return
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
            source = FFmpegPCMAudio(new_file)
            player = voice.play(source)


        #  link = result.loads("link")
        # await ctx.channel.send(str(link))

    # return videosResult


def setup(bot):
    bot.add_cog(MusicManager(bot))
