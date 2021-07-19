import os
import traceback
import discord
import yaml as YAML
from discord.ext import commands

COGS_DIRECTORY = "Cogs"
PREFIX = os.getenv("PREFIX")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, help_command=None, intents=intents)


def load_cogs():
    for cog in os.listdir(COGS_DIRECTORY):
        print(" " * 20)
        directory = f"{COGS_DIRECTORY}/{cog}/"
        cog_file = f"{directory}cog.yml"
        print(f"Walking into {directory}")
        if not os.path.exists(cog_file):
            print(f"{cog_file} does not exist, pass...")
            continue

        print(f"{cog_file} exists, loading cog...")
        with open(cog_file, "r") as stream:
            try:
                yml = YAML.safe_load(stream)
            except YAML.YAMLError as e:
                raise e

            cog_name = yml.get("name", "Unnamed Cog")
            main_cog_file = yml.get("main")
            load = yml.get("load", True)
            if load:
                print(f"Loading {cog_name} cog...")
                try:
                    cog_directory = f"{COGS_DIRECTORY}.{cog}.{main_cog_file}"
                    bot.load_extension(cog_directory)
                    print(f"Cog {cog_name} loaded successfully !")
                except Exception:
                    print(f"Failed to load {cog_name} cog.")
                    traceback.print_exc()


@bot.event
async def on_ready():
    print("Bot ready to use.")
    game = discord.Game(f"{PREFIX}help | Bot à multiple fonctions")
    await bot.change_presence(status=discord.Status.online, activity=game)


if __name__ == "__main__":
    load_cogs()
    bot.run(os.getenv("TOKEN"))
