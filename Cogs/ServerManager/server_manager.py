import asyncio
from datetime import timedelta
from datetime import date
import discord
import datetime
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands


class ServerManager(commands.Cog):
    student_old_learnday = datetime.date(2021, 4, 23)
    student_new_learnday = datetime.date(2021, 7, 22)
    student_id = 600333625887686666

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def day(self, ctx, counter="new"):
        today = datetime.date.today()
        if counter == "new":
            diff = today - self.student_new_learnday
        else:
            diff = today - self.student_old_learnday

        text = f"Day : {diff.days}"
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
    @has_permissions(kick_members=True)
    async def kick_invite(self, ctx, member: discord.User = None, reason=None):
        if member == ctx.message.author:
            await ctx.channel.send("You cannot kick yourself")
        if reason is None:
            reason = "For no reason"
        message = f"You have been kicked from {ctx.guild.name}   {reason}"

        link = await ctx.channel.create_invite(max_age=300)
        try:
            await member.send(f"Here is the link : {link}  ")
        except:
            await ctx.channel.send("Could not invite this member")
        await ctx.guild.kick(member, reason=reason)
        await ctx.channel.send(f"{member} was kick from the server  for  {reason}")

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def unban(self, ctx, *, member):
        try:
            banned_users = await ctx.guild.bans()

            member_name, member_discriminator = member.split('#')
            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    i = 0
                    try:
                        await ctx.guild.unban(user)
                        await ctx.channel.send(f"Unbanned: {user.mention}")
                        i += 1
                    except:
                        if i == 0:
                            await ctx.channel.send("Denied Acces")
        except:
            await ctx.channel.send(f" An error occuried  : {member} is not banned")

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

    @commands.command()
    @has_permissions(manage_roles=True, ban_members=True)
    async def ban_tempo(self, ctx, times, member: discord.User = None, reason=None):
        if "d" in times:
            unity = "d"
            times = str(times).split("d")[0]
            last_time = timedelta(days=int(times))
            sleeping_time = int(times) * 60 * 60 * 24
        if "s" in times:
            unity = "s"
            times = str(times).split("s")[0]
            last_time = timedelta(seconds=int(times))
            sleeping_time = int(times)
        if "h" in times:
            unity = "h"
            times = str(times).split("h")[0]
            last_time = timedelta(hours=int(times))
            sleeping_time = int(times) * 60 * 60
        if "m" in times:
            unity = "m"
            last_time = timedelta(minutes=int(times))
            sleeping_time = int(times) * 60
            times = str(times).split("m")[0]

        if member == ctx.message.author:
            await ctx.channel.send("You cannot ban yourself")
            return
        if reason is None:
            reason = " fun"
        message = f"You have been banned from {ctx.guild.name} for {reason}"
        link = await ctx.channel.create_invite(max_age=300)

        await ctx.channel.send(f"{member} was  banned for {reason}")
        try:
            await member.send(f"Here is the link : {link}  ")
            await member.send(f"You will have the acces to join in {last_time} ")
        except:
            await ctx.channel.send("Could not pm this member")
        await ctx.guild.ban(member, reason=reason)

        await asyncio.sleep(sleeping_time)
        await ctx.guild.unban(member)

def setup(bot):
    bot.add_cog(ServerManager(bot))