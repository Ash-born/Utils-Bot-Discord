import discord
from discord.ext import commands
import os

client = commands.Bot(command_prefix="utils", help_command=None)

@client.event
async def on_ready():
    print('Connected')
PREFIX = "utils "



@client.event
async def on_ready():
    print("Bot ready")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f"{PREFIX}help | Bot à multiple fonctions"))


client.run(os.getenv("TOKEN"))
