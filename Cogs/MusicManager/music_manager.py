from datetime import time

import discord
from discord.ext import commands
import json

from youtubesearchpython import *


class MusicManager(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # def initVideo(self, *args):
    #     videosSearch = VideosSearch(args, limit=2)
    #     return json.dumps(videosSearch.result())

    @commands.command()
    async def play(self, ctx, *args):

        search = VideosSearch(args, limit=1)
        time.sleep(2)
        result = await search.next()

        #  link = result.loads("link")
        # await ctx.channel.send(str(link))
        print(search)
        print("noice")
        await ctx.channel.send(search.next())

    # return videosResult


def setup(bot):
    bot.add_cog(MusicManager(bot))
