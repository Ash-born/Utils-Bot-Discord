import discord

ERROR_EMBED = discord.Embed(
    title=" :bangbang: **Bot found an error during execution**",
    color=discord.Colour.red()
)


def error(reason: str) -> discord.Embed:
    embed = ERROR_EMBED.copy()
    embed.description = reason
    return embed
