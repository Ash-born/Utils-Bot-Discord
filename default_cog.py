# Represents the informations about the cog
YML_FILE = """name: {name}
main: {main}
load: True
"""

# Represents the main file of the cog that will be loaded by bot.load_extension
COG_FILE = """from discord.ext import commands


class {name}(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def help(self, ctx, command: str):
        pass


def setup(bot):
    bot.add_cog({name}(bot))"""

# Represents the default folder that contains all the cogs
DEFAULT_COGS_FOLDER = "cogs/"
