import os

import discord
from discord.ext import commands


class Bot(commands.Bot):

    def __init__(self):
        self.COGS_DIRECTORY = "cogs"
        self.PREFIX = os.getenv("PREFIX")
        intents = discord.Intents.all()
        super().__init__(command_prefix=self.PREFIX, help_command=None, intents=intents)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot ready to use.")
        game = discord.Game(f"{self.PREFIX}help | Bot à multiple fonctions")
        await self.change_presence(status=discord.Status.online, activity=game)
