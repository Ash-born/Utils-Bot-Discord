import yaml
from discord.ext import commands

from bot import Bot


class Debug(commands.Cog):
    debuggers = [
        640847986292949012,
        326806932566310922
    ]

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx: commands.Context, cog_name: str):
        if ctx.author.id not in self.debuggers:
            return

        cogs_directory = self.bot.COGS_DIRECTORY
        with open(f"{cogs_directory}/{cog_name}/cog.yml", "r") as stream:
            yml = yaml.safe_load(stream)

        main_cog_file = yml.get("main")
        cog_dir = f"{cogs_directory}.{cog_name}.{main_cog_file}"
        await ctx.send(f"Reloading {cog_name} cog...")
        self.bot.unload_extension(cog_dir)
        self.bot.load_extension(cog_dir)
        await ctx.send("Finished reloading !")


def setup(bot):
    bot.add_cog(Debug(bot))
