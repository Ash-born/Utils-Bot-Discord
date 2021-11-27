import discord
from cogs.Misc.embeds import error
from discord.ext import commands
from requests.exceptions import RequestException

from cogs.MusicManager.music import Music


class MusicManager(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice = None

    @commands.command()
    async def play(self, ctx: commands.Context, *, args):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send(embed=error("You are not connected to a voice channel"))
            return

        try:
            self.voice = await Music.connect(channel)
            url = ''.join(args)
            await ctx.channel.send(Music.play(url))
        except RequestException:
            await ctx.send(embed=error("Could not find a video with this name."))
        except discord.ClientException:
            await ctx.send(embed=error("The bot is already playing audio. You can stop the session with 'utils stop'."))

    @commands.command()
    async def stop(self, ctx):
        Music.stop(self.voice)
        await ctx.send("Stopped the music.")

    @commands.command()
    async def resume(self, ctx):
        Music.resume(self.voice)
        await ctx.send("Resumed the music.")

    @commands.command()
    async def pause(self, ctx):
        Music.pause(self.voice)
        await ctx.send("Paused the music.")


def setup(bot):
    bot.add_cog(MusicManager(bot))
