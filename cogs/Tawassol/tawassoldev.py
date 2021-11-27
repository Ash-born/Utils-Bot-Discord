from io import BytesIO

import discord
import json
from cogs.Tawassol.tawassol_client import TawassolClient


class TawassolDev(TawassolClient):

    def __init__(self, idclient):
        super().__init__()
        self.__idclient = idclient

    async def connect(self) -> bool:
        self.login["idClient"] = str(self.__idclient)
        self.login["usertype"] = "client"
        self.login["niveau"] = "2"
        self.login["logged_in"] = "true"
        self.connected = True
        return True

    def to_file(self, raw):
        formatted = json.dumps(raw, indent=4).encode("UTF-8")
        file = discord.File(BytesIO(formatted), "request.json")
        return file
