import discord
import shortuuid
from bot import Bot
from datetime import datetime


class Doc:
    DEFAULT_DT_FORMAT = "%m/%d/%Y, %H:%M:%S"
    UUID_LENGTH = 6

    def __init__(self, name: str, title: str, text: str, creator: int, uuid=None, dt=None, color=None, hide=False):
        self.name = name
        self.text = text
        self.title = title
        self.dt = dt or datetime.now().strftime(self.DEFAULT_DT_FORMAT)
        self.creator = creator
        self.uuid = uuid or shortuuid.ShortUUID().random(length=self.UUID_LENGTH)
        self.color = color or 0xffffff
        self.hide = hide or False

    async def generate_embed(self):
        creator = await Bot.instance.fetch_user(self.creator)
        embed = discord.Embed(title=self.title, description=self.text, color=self.color)
        if not self.hide:
            embed.set_author(name=f"Documentation of {creator.display_name}", icon_url=creator.avatar_url)
            embed.set_footer(text=f"{self.name} | Created on {self.dt} | {self.uuid}")

        return embed

    @classmethod
    def serialize(cls, args: dict):
        return cls(args["name"], args["title"], args["text"], args["creator"], args["uuid"], args["dt"], args.get("color"), args.get("hide"))

    def deserialize(self):
        return {
            "name": self.name,
            "title": self.title,
            "text": self.text,
            "creator": self.creator,
            "uuid": self.uuid,
            "dt": self.dt,
            "color": self.color,
            "hide": self.hide
        }
