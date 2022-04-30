import json
import os.path
import discord
from discord.ext import commands
from cogs.Documentation.doc import Doc
from cogs.Misc.embeds import error


class Documentation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cog_dir = self.bot.get_cog_directory(type(self).__name__)
        self.docs_dir = os.path.join(self.cog_dir, "docs.json")
        self.docs = self.load_docs()

    def load_docs(self):
        with open(self.docs_dir, "r") as file:
            return json.load(file)

    def update(self):
        with open(self.docs_dir, "w") as file:
            json.dump(self.docs, file, indent=4)

    def update_doc(self, doc: Doc):
        self.docs[doc.uuid] = doc.deserialize()
        self.update()

    def get_doc(self, uuid: str):
        doc = self.docs.get(uuid)
        if doc:
            return Doc.serialize(doc)

    def modify_doc(self, doc: Doc, new_text: str, creator: int):
        if doc.creator != creator:
            return False

        doc.text = new_text
        self.update_doc(doc)
        return True

    def delete_doc(self, doc: Doc):
        self.docs.pop(doc.uuid)
        self.update()

    @commands.command()
    async def create(self, ctx: commands.Context, name: str, title: str, *, text: str, color: int = 0xffffff, hide: bool = False):
        """
        Command used to create a new documentation.\n
        Takes 2 parameters:
            '**name**': The name of the documentation.\n
            '**title**': The title of the documentation.\n
            '**text**': The actual text of the documentation.
        """
        doc = Doc(name, title, text, ctx.author.id, color, hide)
        self.update_doc(doc)
        await ctx.send(f"Your documentation has been added with the uuid : '{doc.uuid}' ! \
You can access to your documentation by typing '{self.bot.command_prefix}find {doc.uuid}' !")

    @commands.command()
    async def find(self, ctx, uuid: str):
        await ctx.send(f"Searching documentation for uuid '{uuid}'. Please wait...")
        doc = self.get_doc(uuid)
        if doc:
            await ctx.send(embed=await doc.generate_embed())
        else:
            await ctx.send(embed=error(f"Documentation with uuid '{uuid}' not found !"))

    @commands.command()
    async def modify(self, ctx, uuid: str, *, new_text: str):
        doc = self.get_doc(uuid)
        if not doc:
            await ctx.send(embed=error(f"Documentation with uuid '{uuid}' not found !"))
            return

        success = self.modify_doc(doc, new_text, ctx.author.id)
        if success:
            await ctx.send("Your documentation text has been successfully changed !")
        else:
            await ctx.send("You are not the creator of this documentation !")

    @commands.command()
    async def delete(self, ctx, uuid: str):
        doc = self.get_doc(uuid)
        if not doc:
            await ctx.send(embed=error(f"Documentation with uuid '{uuid}' not found !"))
            return

        self.delete_doc(doc)
        await ctx.send(f"Documentation with uuid '{uuid}' has been successfully deleted!")

    @commands.command()
    async def docs(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Documentation(bot))
