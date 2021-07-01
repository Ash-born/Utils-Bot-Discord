import discord
import os
from discord.ext import commands


PREFIX = "utils "
bot = commands.Bot(command_prefix=PREFIX, help_command=None)


@bot.event
async def on_ready():

    print("Bot ready")
    await bot.change_presence(game=discord.Game(f"{PREFIX}help | Bot à multiple fonctions"))


bot.run(os.getenv("TOKEN"))
