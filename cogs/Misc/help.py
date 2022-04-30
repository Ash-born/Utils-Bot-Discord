import discord
from discord.ext import commands
from cogs.Misc.embeds import error


def is_command_in_cog(command: str, cog: commands.Cog):
    for cmd in cog.get_commands():
        if cmd.name == command:
            return cmd

    return False


def get_command_field(command: commands.Command):
    command_doc = command.callback.__doc__ or "*Empty help*"
    params = tuple(command.params)[2:]
    field_name = f"{command.name} "
    if len(params) != 0:
        for param in params:
            field_name += f"[{param}] "
    else:
        field_name += " *(No parameters)*"

    return {
        "name": f"__{field_name}__",
        "value": command_doc,
        "inline": False
    }


def make_help(cog: commands.Cog, command: str = None) -> discord.Embed:
    embed = discord.Embed(title=f"Help of module '{cog.qualified_name}'", color=discord.Colour.red())
    if command:
        cmd = is_command_in_cog(command, cog)
        if not cmd:
            return error(f"Command '**{command}**' not found in module '**{cog.qualified_name}**'")

        embed.set_author(name=f"Help of command '{command}' in module '{cog.qualified_name}'")
        field = get_command_field(cmd)
        embed.title = field.get("name")
        embed.description = field.get("value")
        return embed

    for cmd in cog.get_commands():
        if cmd.hidden:
            continue

        embed.add_field(**get_command_field(cmd))

    return embed
