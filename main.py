import os
import traceback
import yaml
from bot import Bot

bot = Bot()


def load_cogs():
    cogs_directory = bot.COGS_DIRECTORY
    for cog in os.listdir(cogs_directory):
        print(" " * 20)
        directory = f"{cogs_directory}/{cog}/"
        cog_file = f"{directory}cog.yml"
        print(f"Walking into {directory}")
        if not os.path.exists(cog_file):
            print(f"{cog_file} does not exist, pass...")
            continue

        print(f"{cog_file} exists, loading cog...")
        with open(cog_file, "r") as stream:
            try:
                yml = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                raise e

            cog_name = yml.get("name", "Unnamed Cog")
            main_cog_file = yml.get("main")
            load = yml.get("load", True)
            if load:
                print(f"Loading {cog_name} cog...")
                try:
                    cog_directory = f"{cogs_directory}.{cog}.{main_cog_file}"
                    bot.load_extension(cog_directory)
                    print(f"Cog {cog_name} loaded successfully !")
                except Exception:
                    print(f"Failed to load {cog_name} cog.")
                    traceback.print_exc()


if __name__ == "__main__":
    load_cogs()
    bot.run(os.getenv("TOKEN"))
