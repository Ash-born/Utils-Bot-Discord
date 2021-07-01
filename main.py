import discord
from discord.ext import commands
import os
import datetime

PREFIX = "utils"
client = commands.Bot(command_prefix=PREFIX, help_command=None)


@client.event
async def on_ready():
    print("Bot ready")
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game(f"{PREFIX} help | Bot à multiple fonctions"))


@client.event
async def on_message(message):
    if message.content == "day":
        today = datetime.date.today()
        last = datetime.date(2021, 4, 24)
        diff = today - last
        await message.channel.send( f"Days : {diff.days}")

client.run(os.getenv("TOKEN"))
