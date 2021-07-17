import discord
import datetime
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands


class ServerManager(commands.Cog):
    student_learn_day = datetime.date(2021, 4, 23)
    student_id = 600333625887686666

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def days(self, ctx):
        today = datetime.date.today()
        diff = today - self.student_learn_day
        text = f"Days : {diff.days}"
        await ctx.channel.send(text)
        member = ctx.guild.get_member(self.student_id)
        await member.edit(nick=text)

    @commands.command()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.User = None, *, reason=None):
        if member == ctx.message.author:
            await ctx.channel.send("You cannot kick yourself")
        if reason is None:
            reason = "For no reason"
        message = f"You have been kicked from {ctx.guild.name}   {reason}"
        i = 0
        try:
            await ctx.guild.kick(member, reason=reason)
            await ctx.channel.send(f"{member} was kick from the server  for  {reason}")
            i += 1
            await member.send(message)

        except:
            if i == 0:
                await ctx.channel.send("Denied Permession")

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def ban(self, ctx, member: discord.User = None, reason=None):

        if member == ctx.message.author:
            await ctx.channel.send("You cannot ban yourself")
            return
        if reason is None:
            reason = " fun"
        message = f"You have been banned from {ctx.guild.name} for {reason}"
        i = 0
        try:

            await ctx.guild.ban(member, reason=reason)
            await ctx.guild.send(f"{member} was  banned for {reason}")
            i += 1
            await member.send(message)

        except:

            if i == 0:
                await ctx.channel.send("Denied Permession")

def setup(bot):
    bot.add_cog(ServerManager(bot))
