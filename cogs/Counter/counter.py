import json
import os.path
from datetime import datetime
from discord.ext import commands
from cogs.Tawassol.cooldown import Cooldown


class Counter(commands.Cog):
    COUNTERS_DIR = "{cogs_dir}/Counter/counters.json"
    USERS_DIR = "{cogs_dir}/Counter/users.json"
    MAXIMUM_COUNTERS = 2

    def __init__(self, bot):
        self.bot = bot
        self.COUNTERS_DIR = self.COUNTERS_DIR.format(cogs_dir=self.bot.COGS_DIRECTORY)
        self.USERS_DIR = self.USERS_DIR.format(cogs_dir=self.bot.COGS_DIRECTORY)
        self.counters = {}
        self.users = {}
        self.load()

    def load(self):
        self.load_counters()
        self.load_users()

    def load_counters(self):
        if not os.path.isfile(self.COUNTERS_DIR):
            return

        with open(self.COUNTERS_DIR, "r") as counters:
            self.counters = json.load(counters)

    def load_users(self):
        if not os.path.isfile(self.USERS_DIR):
            return

        with open(self.USERS_DIR, "r") as users:
            self.users = json.load(users)

    def update_counters(self):
        with open(self.COUNTERS_DIR, "w") as counter_file:
            json.dump(self.counters, counter_file, default=str, indent=4)

    def update_users(self):
        with open(self.USERS_DIR, "w") as users:
            json.dump(self.users, users, indent=4)

    def remove_counter(self, counter_name: str, counter_author: int):
        c = self.counters.get(counter_name)
        if c and c.get("author") == counter_author:
            self.counters.pop(counter_name)
            self.update_counters()
            return True
        elif not c:
            return False

    def add_counter(self, counter_name: str, counter_author: int, message: str = "", dt: str = None,
                    rename: bool = False,
                    author: int = None):
        if not dt:
            dt = str(datetime.today())

        counter = {
            "author": counter_author,
            "message": message,
            "dt": dt,
            "rename": {
                "canrename": rename,
                "id": author
            }
        }

        self.counters[counter_name] = counter
        self.update_counters()

    def get_user_counters(self, author):
        counters = []
        for counter_name, counter in self.counters.items():
            if counter.get("author") == author:
                counters.append(counter_name)

        return counters

    @commands.command()
    async def test(self, ctx):
        await ctx.send("Hello")

    @commands.command()
    async def counter(self, ctx: commands.Context, counter_name: str):
        cl = Cooldown.check_user("counter", ctx.author.id, 5)
        if not cl[0]:
            await ctx.send(f"Cette commande n'est pas disponible. Réessayez dans {cl[1]}s.")
            return

        counter = self.counters.get(counter_name)
        if not counter:
            await ctx.send("Compteur introuvable.")
            return

        message = counter.get("message")
        today = datetime.today()
        dt = today - datetime.fromisoformat(counter.get("dt"))
        message = f"{message}{dt.days}"
        await ctx.send(message)
        rename = counter.get("rename")
        if rename.get("canrename"):
            author = rename.get("id")
            member = ctx.guild.get_member(int(author))
            await member.edit(nick=message)

    @commands.command()
    async def counters(self, ctx: commands.Context):
        cl = Cooldown.check_user("counters", ctx.author.id, 5)
        if not cl[0]:
            await ctx.send(f"Cette commande n'est pas disponible. Réessayez dans {cl[1]}s.")
            return

        user_counters = self.users.get(str(ctx.author.id), 0)
        await ctx.send(f"Vous avez {user_counters} compteurs.")
        for c in self.get_user_counters(ctx.author.id):
            await ctx.send(f"- {c}")

    @commands.command()
    async def addcounter(self, ctx: commands.Context, counter_name: str, message: str = "", dt: str = None,
                         rename=None, author: str = None):
        cl = Cooldown.check_user("addcounter", ctx.author.id, 5)
        if not cl[0]:
            await ctx.send(f"Cette commande n'est pas disponible. Réessayez dans {cl[1]}s.")
            return

        user_counters = self.users.get(str(ctx.author.id), 0)
        if user_counters >= self.MAXIMUM_COUNTERS:
            await ctx.send("Vous avez dépassé la quantité maximale de compteur que vous pouvez faire !")
            return
        elif user_counters <= 0:
            self.users[str(ctx.author.id)] = 0

        if self.counters.get(counter_name):
            await ctx.send("Ce compteur existe déjà !")
            return

        try:
            datetime.fromisoformat(dt)
        except ValueError:
            await ctx.send("La date indiquée n'est pas valide. Veuillez en saisir un au format iso.")
            return

        if rename and not author or not author.isdigit():
            author = ctx.author.id

        self.add_counter(counter_name, ctx.author.id, message, dt, rename, author)
        self.users[str(ctx.author.id)] += 1
        self.update_users()
        await ctx.send("Votre compteur a bien été ajouté !")

    @commands.command()
    async def removecounter(self, ctx: commands.Context, counter_name: str):
        cl = Cooldown.check_user("removecounter", ctx.author.id, 5)
        if not cl[0]:
            await ctx.send(f"Cette commande n'est pas disponible. Réessayez dans {cl[1]}s.")
            return

        removed = self.remove_counter(counter_name, ctx.author.id)
        if removed:
            await ctx.send("Votre compteur a bien été retiré !")
            self.users[str(ctx.author.id)] -= 1
            self.update_users()
        elif not removed:
            await ctx.send("Ce compteur n'existe pas.")
        else:
            await ctx.send("Vous n'avez pas le droit de retirer ce compteur.")


def setup(bot):
    bot.add_cog(Counter(bot))
