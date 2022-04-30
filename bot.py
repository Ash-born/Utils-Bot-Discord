import os
import yaml
import asyncio
import logging
import discord
from io import StringIO
from discord.ext import commands
from cogs.Misc.embeds import error
from cogs.Misc.help import make_help
from cogs.Misc.page import Page

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    instance = None
    FORMAT = "[%(asctime)s](%(name)s): %(message)s"
    MAX_COGS_HELP = 6
    MAX_COMMANDS_HELP = 8
    debuggers = [
        640847986292949012,
        326806932566310922
    ]

    def __init__(self, args=None):
        self.args = args
        self.COGS_DIRECTORY = "cogs"
        self.PREFIX = None
        self.TOKEN = None
        self.DEBUG = None
        self.logs = StringIO()
        self.process_args()

        Bot.instance = self
        intents = discord.Intents.all()
        super().__init__(command_prefix=self.PREFIX, help_command=None, intents=intents)
        self.add_command(commands.Command(self.help, name="help"))

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Bot ready to use.")
        game = discord.Game(f"{self.PREFIX}help | Bot à multiple fonctions")
        await self.change_presence(status=discord.Status.online, activity=game)

    async def help(self, ctx: commands.Context, module: str = None, command: str = None):
        if module is None:
            embed = discord.Embed(
                title="Voici tous les modules disponibles avec leurs commandes !",
                color=discord.Color.orange()
            )
            cogs_help_count = self.MAX_COGS_HELP
            if cogs_help_count > len(self.cogs):
                cogs_help_count = len(self.cogs)

            start = 0
            bonus = cogs_help_count
            len_cogs = len(self.cogs)
            page = Page(0, len_cogs, bonus)

            def check(reaction: discord.Reaction, user: discord.User) -> bool:
                return user == ctx.author and reaction.emoji in ("⬅️", "➡️")

            while True:
                embed.clear_fields()
                embed = self.generate_help_embed(start, start + bonus, embed)
                embed_msg = await ctx.send(embed=embed)

                await embed_msg.add_reaction("⬅️")
                await embed_msg.add_reaction("➡️")
                try:
                    reaction, user = await self.wait_for("reaction_add", timeout=5, check=check)
                    if reaction.emoji == "⬅️":
                        start, last_start = page.last()
                        if start == last_start:
                            break

                    else:
                        start, last_start = page.next()
                        if start == last_start:
                            break

                    continue
                except asyncio.TimeoutError as e:
                    logger.debug(e)
                    return
        else:
            cog = self.get_cog(module)
            if cog is None or getattr(cog, "hidden", False):
                await ctx.send(embed=error(f"Ce module est introuvable. Veuillez en renseigner un ou taper '{self.PREFIX}help'"))
                return

            cog_help_func = getattr(cog, "help", False)
            if not cog_help_func:
                await ctx.send(embed=make_help(cog, command))
                return

            try:
                await cog_help_func(ctx, command)
            except Exception as e:
                logger.exception(f"Exception :", exc_info=e)
                await ctx.send(embed=error("Une erreur est survenue en essayant d'afficher l'aide du module. :rage:"))

    def generate_help_embed(self, start: int, end: int, embed: discord.Embed = None):
        if embed is None:
            embed = discord.Embed()

        cogs = tuple(self.cogs.items())
        for cog_name, cog in cogs[start: end]:
            if getattr(cog, "hidden", False):
                continue

            cog_commands = ""
            cmds = cog.get_commands()
            cmds_help_count = min(self.MAX_COMMANDS_HELP, len(cmds))

            for cmd in cmds[: cmds_help_count]:
                if cmd.hidden:
                    continue

                cog_commands += f"- *{cmd.name}*\n"

            embed.add_field(name=f"**{cog_name}** :", value=cog_commands)

        return embed

    def get_cog_directory(self, cog_name: str):
        return os.path.join(self.COGS_DIRECTORY, cog_name)

    def process_args(self):
        args = self.args
        if not args:
            return

        self.TOKEN = args.get("token") or os.getenv("TOKEN")
        self.PREFIX = args.get("prefix") or os.getenv("PREFIX")

        self.DEBUG = args.get("debug") or __debug__
        level = logging.DEBUG if self.DEBUG else logging.INFO
        file_handler = logging.FileHandler(filename="debug.log", mode="a", encoding="UTF-8")
        logs_stream_handler = logging.StreamHandler(self.logs)
        logging.basicConfig(
            level=level,
            format=self.FORMAT,
            handlers=[
                file_handler,
                logs_stream_handler,
                logging.StreamHandler()
            ]
        )

    def load_cogs(self):
        cogs_directory = self.COGS_DIRECTORY
        for cog in os.listdir(cogs_directory):
            logger.debug(" " * 20)
            directory = self.get_cog_directory(cog)
            cog_file = os.path.join(directory, "cog.yml")
            logger.info(f"Walking into {directory}")
            if not os.path.exists(cog_file):
                logger.debug(f"{cog_file} does not exist, pass...")
                continue

            logger.debug(f"{cog_file} exists, loading cog...")
            with open(cog_file, "r") as stream:
                yml = yaml.safe_load(stream)
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
