import discord
import asyncio
from discord.ext import commands
from cogs.Tawassol.tawassol_client import TawassolClient
from cogs.Tawassol.tawassoldev import TawassolDev
from cogs.Tawassol.cooldown import Cooldown
from io import BytesIO


class Tawassol(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.clients = {}
        self.devs = {}
        self.admins = [640847986292949012, 326806932566310922]

    async def help(self, ctx):
        p = self.bot.command_prefix
        embed = discord.Embed(title="Voici la liste de toutes les commandes disponibles !", color=discord.Color.red())

        embed.add_field(
            name=f"__{p}login 'identifiant' 'mot de passe'__",
            value="Commande qui permet de se connecter à Tawassol.",
            inline=False
        )

        embed.add_field(
            name=f"__{p}logout__",
            value="Commande qui permet de se déconnecter de Tawassol.",
            inline=False
        )

        embed.add_field(
            name=f"__{p}messages 'début' 'fin'__",
            value=f"""
    Commande qui affiche les messages entre un intervale de départ et de fin depuis un compte Tawassol.
    :warning: **Nécessite d'être identifié à l'aide de {p}login.**
    Prends 2 arguments optionnels:
        - **"début"**: Un entier indiquant la valeur de départ, elle est égale à 0 par défaut.
        - **"fin"**: Un entier indiquant la valeur de fin, elle est égale à 5 par défaut.""",
            inline=False
        )

        embed.add_field(
            name=f"__{p}confs__",
            value=f"""
    Commande qui affiche les vidéos-conférences disponibles depuis un compte Tawassol.
    **:warning: Nécessite d'être identifié à l'aide de {p}login.**""",
            inline=False)

        embed.add_field(
            name=f"__{p}lastconf__",
            value=
            f"""Commande qui affiche la dernière vidéo-conférence disponible depuis un compte Tawassol.
            **:warning: Nécessite d'être identifié à l'aide de {p}login.**""",
            inline=False
        )

        embed.add_field(
            name=f"__{p}zip__",
            value=
            f"""Commande qui renvoie un zip contenant tous les messages depuis un compte Tawassol.
            **:warning: Nécessite d'être identifié à l'aide de {p}login.**""",
            inline=False
        )

        embed.add_field(
            name=f"__{p}checker__",
            value=
            f"""Commande qui envoie un message privé à l'utilisateur lorsqu'il reçoit un message dans Tawassol.
            **:warning: Nécessite d'être identifié à l'aide de {p}login.**""",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, type=commands.BucketType.user)
    @commands.command()
    async def login(self, ctx: commands.Context, code: str = None, mdp: str = None):
        await ctx.message.delete()
        client = self.clients.get(ctx.author.id)
        if client and client.connected:
            await ctx.send("Vous êtes déjà connectés !")
            return

        if None in (code, mdp):
            await ctx.send("Vous n'avez pas entré d'identifiant et/ou de mot de passe")
            return

        await ctx.send("Connexion à votre compte tawassol...")
        code = code.strip("|")
        mdp = mdp.strip("|")

        client = TawassolClient(code, mdp)
        connected = await client.connect()
        if connected:
            self.clients[ctx.author.id] = client
            await ctx.send("Connexion réussie !")
        else:
            await client.disconnect()
            await ctx.send("Connexion échouée, réessayez une autre fois")

    @commands.cooldown(1, 5, type=commands.BucketType.user)
    @commands.command()
    async def logindev(self, ctx, idclient: str):
        await ctx.message.delete()
        if ctx.author.id not in self.admins:
            await ctx.send("Vous n'êtes pas autorisé à exécuter cette commande !")
            return

        dev = self.clients.get(ctx.author.id)
        if dev and dev.connected:
            await ctx.send("Vous êtes déjà connectés !")
            return

        if idclient is None:
            await ctx.send("Vous n'avez pas entré d'idclient")
            return

        idclient = idclient.strip()
        if not idclient.isdigit():
            await ctx.send("L'idclient entré n'est pas valide")
            return

        await ctx.send("Connexion à votre compte tawassol...")

        dev = TawassolDev(idclient)
        connected = await dev.connect()
        if connected:
            self.clients[ctx.author.id] = dev
            await ctx.send("Connexion réussie !")
        else:
            await dev.disconnect()
            await ctx.send("Connexion échouée, réessayez une autre fois")

    @commands.command()
    async def logout(self, ctx: commands.Context):
        client = self.clients.get(ctx.author.id)
        if client is None:
            await ctx.send(f"Vous n'êtes pas encore connecté ! Connectez-vous avec la commande {self.bot.command_prefix}login")
            return

        await client.disconnect()
        self.clients.pop(ctx.author.id)
        await ctx.send("Vous avez bien été déconnectés !")

    @commands.command()
    async def messages(self, ctx: commands.Context, start: int = 0, end: int = 5):
        client = self.clients.get(ctx.author.id)
        if client is None or not client.connected:
            await ctx.send("Vous n'êtes pas encore connecté ! Connectez-vous avec la commande taw login")
            return

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return user == ctx.author and reaction.emoji in ("⬅️", "➡️")

        if isinstance(client, TawassolDev):
            raw_json = await client.get_messages(True)
            await ctx.author.send(file=client.to_file(raw_json))
            messages = raw_json.get("messages")
        else:
            messages = await client.get_messages()
        if not start < end <= len(messages):
            if len(messages) <= 0:
                await ctx.send("Il n'y a aucun message à afficher.")
                return

            start = 0
            end = len(messages)

        cl = Cooldown.check_user("messages", ctx.author.id, 10)
        if not cl[0]:
            await ctx.send(f"Cette commande n'est pas disponible. Réessayez dans {cl[1]}s.")
            return

        bonus = end - start
        last_start = start
        while True:
            embed = client.generate_messages_embed(start, start + bonus, messages)
            try:
                embed_msg = await ctx.send(embed=embed)
            except discord.HTTPException:
                await ctx.send(
                    "Les messages trop nombreux pour être affichés, veuillez indiquer une valeur de départ et/ou de fin"
                    "plus petites")
                return

            await embed_msg.add_reaction("⬅️")
            await embed_msg.add_reaction("➡️")
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=check)
                if reaction.emoji == "⬅️":
                    start -= bonus
                    if start < start + bonus < bonus:
                        start = 0
                        if last_start == start:
                            break

                    last_start = start
                else:
                    start += bonus
                    if start < start + bonus > len(messages):
                        start = len(messages) - bonus
                        if last_start == start:
                            break

                    last_start = start
                continue
            except asyncio.TimeoutError as e:
                print(e)

            break

    @commands.command()
    async def confs(self, ctx: commands.Context):
        client = self.clients.get(ctx.author.id)
        if client is None or not client.connected:
            await ctx.send(f"Vous n'êtes pas encore connecté ! Connectez-vous avec la commande {self.bot.command_prefix}login")
            return

        cl = Cooldown.check_user("confs", ctx.author.id, 10)
        if not cl[0]:
            await ctx.send(f"Cette commande n'est pas disponible. Réessayez dans {cl[1]}s.")
            return

        if isinstance(client, TawassolDev):
            raw_json = await client.get_conferences(True)
            await ctx.author.send(file=client.to_file(raw_json))
            conferences = raw_json.get("videoConference")
        else:
            conferences = await client.get_conferences()
        embed = discord.Embed(title=f"Résultats {0}-{len(conferences)}", color=discord.Color.green())
        for conf in conferences:
            subject = conf.get("matiere")
            date = conf.get("date")
            content = conf.get("object")
            link = conf.get("join_url")
            content += f"\n[Rejoindre la conférence]({link})"

            embed.add_field(name=f"__{subject} - {date}__", value=content, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def lastconf(self, ctx: commands.Context):
        client = self.clients.get(ctx.author.id)
        if client is None or not client.connected:
            await ctx.send(f"Vous n'êtes pas encore connecté ! Connectez-vous avec la commande {self.bot.command_prefix}login")
            return

        cl = Cooldown.check_user("lastconf", ctx.author.id, 10)
        if not cl[0]:
            await ctx.send(f"Cette commande n'est pas disponible. Réessayez dans {cl[1]}s.")
            return

        confs = await client.get_conferences()
        if len(confs) <= 0:
            await ctx.send("Il n'y a aucune conférence à afficher. :frowning:")
            return

        conf = confs[0]
        embed = discord.Embed(title="La dernière conférence disponible !", color=discord.Color.green())
        subject = conf.get("matiere")
        date = conf.get("date")
        content = conf.get("object")
        link = conf.get("join_url")
        content += f"\n[Rejoindre la conférence]({link})"

        embed.add_field(name=f"__{subject} - {date}__", value=content, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def zip(self, ctx: commands.Context):
        client = self.clients.get(ctx.author.id)
        if client is None or not client.connected:
            await ctx.send(f"Vous n'êtes pas encore connecté ! Connectez-vous avec la commande {self.bot.command_prefix}login")
            return

        cl = Cooldown.check_user("zip", ctx.author.id, 10)
        if not cl[0]:
            await ctx.send(f"Cette commande n'est pas disponible. Réessayez dans {cl[1]:.2f}s.")
            return

        try:
            await ctx.send("Génération du zip en cours...")
            zip_out = await client.zip_messages()
            if not zip_out.getbuffer():
                await ctx.send("Erreur durant la génération du zip, veuillez réessayer plus tard")
                return

            out = BytesIO(zip_out.getbuffer())
            out.name = zip_out.name

            file = discord.File(out)
            await ctx.send("Voici le zip contenant tout vos messages !", file=file)

            out.close()
            file.close()
        except Exception as e:
            print(e)

    @commands.command()
    async def checker(self, ctx: commands.Context):
        client = self.clients.get(ctx.author.id)
        if client is None or not client.connected:
            await ctx.send(f"Vous n'êtes pas encore connecté ! Connectez-vous avec la commande {self.bot.command_prefix}login")
            return

        if client.running:
            client.running = False
            await ctx.send("Votre checker a été désactivé !")
        else:
            cl = Cooldown.check_user("checker", ctx.author.id, 60)
            if not cl[0]:
                await ctx.send(f"Cette commande n'est pas disponible. Réessayez dans {cl[1]:.2f}s.")
                return

            client.running = True
            await ctx.send("Votre checker a été activé !")
            await client.check_msg_listener(ctx.author)


def setup(bot):
    bot.add_cog(Tawassol(bot))
