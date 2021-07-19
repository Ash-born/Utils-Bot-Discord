import asyncio

import discord
from discord.ext import commands
from datetime import timedelta
import datetime as dt
import random
import pytz
from discord.ext.commands import has_permissions


class Giveaway(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @has_permissions(administrator=True)
    async def giveaway(self, ctx, times , *price):
      try :
            if "d" in times:
                unity = "d"
                times = str(times).split("d")[0]
            if "s" in times:
                unity = "s"
                times = str(times).split("s")[0]
            if "h" in times:
                unity = "h"
                times = str(times).split("h")[0]
            if "m" in times:
                unity = "m"

                times = str(times).split("m")[0]

            if int(times) == times:
                await ctx.channel.send("Time should be a number")
                return

            if unity == 'd':
                last_time = timedelta(days=int(times))
                sleeping_time = int(times) *60  *60*24
            if unity == 's':
                last_time = timedelta(seconds=int(times))
                sleeping_time = int(times)
            if unity == 'm':
                last_time = timedelta(minutes=int(times))
                sleeping_time = int(times) * 60
            if unity == 'h':
                last_time = timedelta(hours=int(times))
                sleeping_time = int(times) * 60 * 60

            if "d" in times:
                unity = "d"
                times = str(times).split("d")[0]
            if "s" in times:
                unity = "s"
                times = str(times).split("s")[0]
            if "h" in times:
                unity = "h"
                times = str(times).split("h")[0]
            if "m" in times:
                unity = "m"

                times = str(times).split("m")[0]

            if int(times) == times:
                await ctx.channel.send("Time should be a number")
                return

            if unity == 'd':
                last_time = timedelta(days=int(times))
                sleeping_time = int(times) *60  *60*24
            if unity == 's':
                last_time = timedelta(seconds=int(times))
                sleeping_time = int(times)
            if unity == 'm':
                last_time = timedelta(minutes=int(times))
                sleeping_time = int(times) * 60
            if unity == 'h':
                last_time = timedelta(hours=int(times))
                sleeping_time = int(times) * 60 * 60

            a = ""
            t = dt.datetime.now()
            new_time = t + last_time
            for i in price:
                a += i + " "
            await ctx.message.delete()
            embed = discord.Embed(title=f"🎉 {a} 🎉"
                                  , description=f"Time remaining is : {last_time}",
                                  color=0x8c82d3)
            embed.add_field(name="Expected to finish at : ", value=f"{new_time.date()} at {new_time.hour}:{new_time.minute}:{new_time.second}", inline=True)

            test = await ctx.send(embed=embed)
            await test.add_reaction("🎉")

            await asyncio.sleep(sleeping_time)
            nouveau = dt.datetime.now()
            if nouveau >= new_time:
                print(dt.datetime.now() + last_time)
                players = []
                message = await ctx.fetch_message(test.id)
                for reaction in message.reactions:
                    if reaction.emoji == '🎉':
                        async for user in reaction.users():
                            if user != self.bot.user:
                                players.append(user.mention)

                if len(players) < 2:
                    await ctx.send('Time is up, and not enough players')
                else:
                    await ctx.send(players)
                    try:
                        rd = random.randint(0, len(players) - 1)
                        winner = players[rd]
                        embed = discord.Embed(title="GIVEAWAY ENDED", description=f"Congratulations {winner} you won ",
                                              color=0x2d9f7d)
                        embed.add_field(name="winner : ", value=winner, inline=True)
                        embed.add_field(name="Hosted by : ", value=f"@{ctx.message.author}", inline=True)
                        embed.add_field(name="Prize : ", value=a, inline=True)
                        embed.set_footer(text=f"Ended at {nouveau}")
                        await ctx.send(embed=embed)
                    except:
                        await ctx.send("Not enough players")
      except :
            await ctx.send("Error found : Invalide Syntaxe ")

def setup(bot):
    bot.add_cog(Giveaway(bot))
