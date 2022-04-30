import yaml
import logging
import discord
from discord.ext import commands
from bot import Bot

logger = logging.getLogger(__name__)


class Debug(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.debuggers = self.bot.debuggers
        self.hidden = True

    @commands.command(hidden=True)
    async def reload(self, ctx: commands.Context, cog_name: str):
        if ctx.author.id not in self.debuggers:
            return

        cogs_directory = self.bot.COGS_DIRECTORY
        with open(f"{cogs_directory}/{cog_name}/cog.yml", "r") as stream:
            yml = yaml.safe_load(stream)

        main_cog_file = yml.get("main")
        cog_dir = f"{cogs_directory}.{cog_name}.{main_cog_file}"
        await ctx.send(f"Reloading {cog_name} cog...")
        self.bot.reload_extension(cog_dir)
        await ctx.send("Finished reloading !")

    @commands.command(hidden=True)
    async def logs(self, ctx: commands.Context, lines_count: int = 10):
        if ctx.author.id not in self.debuggers:
            return

        embed = discord.Embed(
            title="**Logs**",
            color=discord.Color.light_grey()
        )
        self.bot.logs.seek(0)
        logs = ''.join(self.bot.logs.readlines(lines_count))
        embed.description = f"""
```
{logs}
```
"""
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Debug(bot))
