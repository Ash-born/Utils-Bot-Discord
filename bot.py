import logging
import os
import discord
import yaml
from discord.ext import commands

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    instance = None
    FORMAT = "[%(asctime)s](%(name)s): %(message)s"

    def __init__(self, args=None):
        self.args = args
        self.COGS_DIRECTORY = "cogs"
        self.PREFIX = None
        self.TOKEN = None
        self.DEBUG = None
        self.process_args()

        Bot.instance = self
        intents = discord.Intents.all()
        super().__init__(command_prefix=self.PREFIX, help_command=None, intents=intents)

    def process_args(self):
        args = self.args
        if not args:
            return

        self.TOKEN = args.get("token") or os.getenv("TOKEN")
        self.PREFIX = args.get("prefix") or os.getenv("PREFIX")
        self.DEBUG = args.get("debug") or __debug__
        logging.basicConfig(level=logging.DEBUG if self.DEBUG else logging.INFO, format=self.FORMAT)

    def load_cogs(self):
        cogs_directory = self.COGS_DIRECTORY
        for cog in os.listdir(cogs_directory):
            logger.debug(" " * 20)
            directory = f"{cogs_directory}/{cog}/"
            cog_file = f"{directory}cog.yml"
            logger.info(f"Walking into {directory}")
            if not os.path.exists(cog_file):
                logger.debug(f"{cog_file} does not exist, pass...")
                continue

            logger.debug(f"{cog_file} exists, loading cog...")
            with open(cog_file, "r") as stream:
                try:
                    yml = yaml.safe_load(stream)
                except yaml.YAMLError as e:
                    raise e

                cog_name = yml.get("name", "Unnamed Cog")
                main_cog_file = yml.get("main")
                load = yml.get("load", True)
                load_debug = yml.get("load_debug", False)
                if load:
                    if load_debug and not self.DEBUG:
                        logger.info(f"Cannot load {cog_name} cog because the bot is running in production mode.")
                        continue

                    logger.info(f"Loading {cog_name} cog...")
                    try:
                        cog_directory = f"{cogs_directory}.{cog}.{main_cog_file}"
                        self.load_extension(cog_directory)
                        logger.info(f"Cog {cog_name} loaded successfully !")
                    except Exception as e:
                        logger.exception(f"Failed to load {cog_name} cog.", e)

    def run_bot(self):
        self.load_cogs()
        self.run(self.TOKEN)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Bot ready to use.")
        game = discord.Game(f"{self.PREFIX}help | Bot à multiple fonctions")
        await self.change_presence(status=discord.Status.online, activity=game)
