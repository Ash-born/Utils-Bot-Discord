import discord
import aiohttp
import asyncio
import uuid
from markdownify import markdownify
from zipfile import ZipFile
from io import BytesIO

html_href = "\n<a href={link}>📁 Pièce jointe</a>"
html_file = """
<meta charset="UTF-8">
<h1><u>{header}</u></h1>
<div>{content}</div>
"""

class URL:
    TAWASSOLAPI = "https://tawassolapp.com/myspaceApi/"
    LOGIN = f"{TAWASSOLAPI}connecte/"
    GETMESSAGES = f"{TAWASSOLAPI}getMessages/"
    GETCONFERENCE = f"{TAWASSOLAPI}getVideoConference/"
    ADDVUTOMSG = f"{TAWASSOLAPI}addVuToMessage/"


class TawassolClient:

    def __init__(self, code: str = None, mdp: str = None):
        self._code = code
        self.__mdp = mdp
        self.connected = False
        self.login = {}
        self.running = False
        self.session = aiohttp.ClientSession()

    def get_login_json(self):
        return {
            "code": self._code,
            "password": self.__mdp
        }

    def get_usersession_json(self):
        return {
            "userSession[usertype]": self.login.get("usertype"),
            "userSession[idClient]": self.login.get("idClient"),
            "userSession[niveau]": self.login.get("niveau"),
            "userSession[logged_in]": self.login.get("logged_in")
        }

    async def connect(self) -> bool:
        try:
            async with self.session.post(URL.LOGIN, data=self.get_login_json(), timeout=5) as login:
                if login.status != 200:
                    return False

                json = await login.json(content_type=None)
                if json.get("success"):
                    self.login = json.get("userData").get("userSession")
                    self.connected = True
                    return True

        except aiohttp.ClientError:
            pass

        return False

    async def disconnect(self):
        self.login = None
        self._code = None
        self.__mdp = None
        self.connected = None
        self.running = None
        await self.session.close()
        self.session = None

    async def get_conferences(self) -> list:
        try:
            async with self.session.post(URL.GETCONFERENCE, data=self.get_usersession_json(), timeout=5) as confs:
                if confs.status == 200:
                    confs_json = await confs.json(content_type=None)
                    return confs_json.get("videoConference")

        except aiohttp.ClientError:
            return []

    async def get_messages(self) -> list:
        try:
            async with self.session.post(URL.GETMESSAGES, data=self.get_usersession_json(), timeout=5) as messages:
                if messages.status == 200:
                    msg_json = await messages.json(content_type=None)
                    return msg_json.get("messages")

        except aiohttp.ClientError:
            return []

    async def add_vu_to_msg(self, message: dict):
        url = f"{URL.ADDVUTOMSG}{message['idMessage']}/{self.login['idClient']}"
        try:
            async with self.session.post(url, data=self.get_usersession_json(), timeout=5) as rq:
                pass

        except aiohttp.ClientError:
            pass

    async def check_msg_listener(self, user):
        while self.running:
            messages = await self.get_messages()
            for message in messages:
                vu = message.get("vu")
                if vu:
                    continue

                embed = discord.Embed(title=f"Vous avez reçu un nouveau message !", color=discord.Color.red())

                subject = message.get("matiere") or message.get("from")
                date = message.get("time")
                content = markdownify(message.get("content")) or "*Message vide*"
                if len(content) > 1023:
                    content = content[:1020] + "..."

                file = message.get("file")
                if file:
                    content += f"\n:file_folder: [Pièce jointe]({file})"

                embed.add_field(name=f"__{subject} - {date}__", value=content, inline=False)
                await user.send(embed=embed)
                await self.add_vu_to_msg(message)

            await asyncio.sleep(300)

    async def zip_messages(self) -> BytesIO:
        messages = await self.get_messages()
        out = BytesIO()
        out.name = f"{uuid.uuid4()}.zip"
        with ZipFile(out, "w") as zipmsg:
            for message in messages:
                link = message.get("file")
                if not link:
                    continue

                subject = message.get("matiere")
                if not subject:
                    subject = message.get("from")

                date = message.get("time")
                content = message.get("content") or "Message vide."
                messageid = message.get("idMessage")

                header = f"{subject} - {date}"
                html = html_file.format(header=header, content=content) + html_href.format(link=link)

                date = date.replace("/", "-")
                fname = f"{date}_{messageid}"
                zipmsg.writestr(f"{subject}/{fname}.html", html)

        return out

    async def generate_messages_embed(self, start: int, end: int, messages: list) -> discord.Embed:
        embed = discord.Embed(title=f"Résultats {start}-{end} sur un total de {len(messages)}",
                              color=discord.Color.green())
        for i in range(start, end):
            message = messages[i]
            subject = message.get("matiere") or message.get("from")
            date = message.get("time")
            content = markdownify(message.get("content")) or "*Message vide*"
            if len(content) > 1023:
                content = content[:1023]
            file = message.get("file")
            if file:
                content += f"\n:file_folder: [Pièce jointe]({file})"

            embed.add_field(name=f"__{subject} - {date}__", value=content, inline=False)

        return embed
