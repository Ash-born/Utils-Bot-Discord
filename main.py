import discord
from discord.ext import commands
import os

from server_manager import ServerManager
PREFIX = "utils "
client = commands.Bot(command_prefix=PREFIX)


@client.event
async def on_ready():
    print("Bot ready")
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game(f"{PREFIX}help | Bot à multiple fonctions")
                                 )



client.add_cog(ServerManager(client))
client.run(os.getenv("TOKEN"))
