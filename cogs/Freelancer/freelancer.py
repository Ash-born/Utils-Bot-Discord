import asyncio
import json
import os

import discord
import websockets as wss
from discord.ext import commands
from discord.ext.commands import BucketType
from freelancersdk.resources.projects import *
from freelancersdk.resources.users import get_self_user_id
from freelancersdk.session import Session

from cogs.Misc.embeds import error
from cogs.Misc.page import Page


class Freelancer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        token = os.getenv("FREELANCER_TOKEN")
        self.session = Session(oauth_token=token)
        self.dir = self.bot.get_cog_directory("Freelancer")
        self.running = False
        self.viewed_projects = {}

    @commands.command()
    async def startpoll(self, ctx):
        if ctx.author.id not in self.bot.debuggers or self.running:
            return

        self.running = True
        while self.running:
            try:
                projects = self.get_projects(5)
            except:
                continue

            for project in projects:
                project_id = project["id"]
                if not self.viewed_projects.get(project_id):
                    for debugger in self.bot.debuggers:
                        user = self.bot.get_user(debugger)
                        if user:
                            try:
                                await user.send(embed=self.get_project_embed(project))
                                self.viewed_projects[project_id] = True
                            except Exception:
                                pass

            await asyncio.sleep(30)

    @commands.command()
    async def stoppoll(self, ctx):
        if ctx.author.id not in self.bot.debuggers or self.running:
            return

        self.running = False
        await ctx.send("Successfully stopped polling projects !")

    @commands.command()
    async def price(self, ctx, project_id: int, price: int, period: int, *, message):
        if ctx.author.id not in self.bot.debuggers:
            return

        my_user_id = get_self_user_id(self.session)
        bid_data = {
            'project_id': project_id,
            'bidder_id': my_user_id,
            'amount': price,
            'period': period,
            'milestone_percentage': 100,
            'description': message,
        }
        try:
            place_project_bid(self.session, **bid_data)
            await ctx.send("Placed bid successfully !")
        except BidNotPlacedException as e:
            await ctx.send(f"Could not place bid. Error message: {e} | Error code: {e.error_code}")

    @commands.cooldown(1, 1, BucketType.user)
    @commands.command()
    async def projects(self, ctx: commands.Context):
        limit = 10
        search_filter = create_search_projects_filter(
            sort_field='time_updated',
            or_search_query=True,
            project_types="fixed",
            languages=["en", "fr"],
            jobs=[
                9,     # JavaScript
                10,    # XML,
                13,    # Python,
                15,    # .NET,
                112,   # JavaFX,
                7,     # Java,
                106,   # C# Programming,
                901,   # JSON
                30,    # System Admin
                36,    # Data Processing
                55,    # Excel
                72,    # Twitter
                95,    # Web Scraping
                158,   # PDF
                2657,  # Discord
                2651,  # QR Code Making
                2380,  # Telegram API
            ]
        )

        project_details = create_get_projects_project_details_object(jobs=True, full_description=True)

        try:
            p = search_projects(
                self.session,
                query="",
                search_filter=search_filter,
                project_details=project_details,
                limit=limit,
                active_only=True,
            )
            projects = p["projects"]
        except ProjectsNotFoundException as e:
            await ctx.send(embed=error(
                f"Error occured during request.\nError message: '{e.message}'\nServer response: {e.error_code}\n"
                f"Please try later..."))
            return

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return user == ctx.author and reaction.emoji in ("⬅️", "➡️")

        page = Page(0, limit, 1)
        start = 0
        while True:
            embed_msg = await ctx.send(embed=self.get_project_embed(projects[start]))
            await embed_msg.add_reaction("⬅️")
            await embed_msg.add_reaction("➡️")
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=5, check=check)
                if reaction.emoji == "⬅️":
                    start, last_start = page.last()
                    if start == last_start:
                        break

                else:
                    start, last_start = page.next()
                    if start == last_start:
                        break

                continue
            except asyncio.TimeoutError:
                return

    def get_projects(self, limit=10):
        search_filter = create_search_projects_filter(
            sort_field='time_updated',
            or_search_query=True,
            project_types="fixed",
            languages=["en", "fr"],
            jobs=[
                9,  # JavaScript
                10,  # XML,
                13,  # Python,
                15,  # .NET,
                112,  # JavaFX,
                7,  # Java,
                106,  # C# Programming,
                901,  # JSON
            ]
        )

        project_details = create_get_projects_project_details_object(jobs=True, full_description=True)

        try:
            p = search_projects(
                self.session,
                query="",
                search_filter=search_filter,
                project_details=project_details,
                limit=limit,
                active_only=True,
            )
            return p["projects"]
        except ProjectsNotFoundException as e:
            return []

    def get_project_embed(self, project: dict):
        description = project["description"]
        embed = discord.Embed(title=project["title"],
                              url=f"https://www.freelancer.com/projects/{project['seo_url']}",
                              description=description)

        jobs = project["jobs"]
        skills = ""
        for job in jobs:
            skills += f"- {job['name']}\n"

        embed.add_field(name="Necessary skills", value=skills, inline=True)

        # currency
        curr = project["currency"]["sign"]
        budget = project["budget"]
        budget_price = f"{budget['minimum']}{curr}-{budget['maximum']}{curr}"
        embed.add_field(name="Budget price", value=budget_price, inline=True)

        stats = project["bid_stats"]
        embed.add_field(name="Bid counts", value=stats["bid_count"], inline=True)
        embed.add_field(name="Bid average", value=f'{stats["bid_avg"]}{curr}', inline=True)
        embed.set_footer(text=f"Bid Id: {project['id']}")
        return embed


def setup(bot):
    bot.add_cog(Freelancer(bot))
