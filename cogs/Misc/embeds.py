from discord import Embed, Colour

ERROR_EMBED = Embed(
    title=" :bangbang: **Bot found an error during execution**",
    color=Colour.red()
)


def error(reason: str) -> Embed:
    embed = ERROR_EMBED.copy()
    embed.description = reason
    return embed
