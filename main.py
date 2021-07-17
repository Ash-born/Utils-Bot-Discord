import discord
import os
from discord.ext import commands


extensions = [
  "tawassol",
  "morpion",
  "server_manager",
]

intents = discord.Intents.all()
PREFIX = "utils "
bot = commands.Bot(command_prefix=PREFIX, help_command=None, intents=intents)


if __name__ == "__main__":
    for extension in extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():

    print("Bot ready")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"{PREFIX}help | Bot à multiple fonctions"))

bot.run(os.getenv("TOKEN"))
