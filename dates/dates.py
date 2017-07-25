import discord
import asyncio
import re
import os
from discord.ext import commands
from .utils.dataIO import dataIO
from __main__ import send_cmd_help

class Dates:

    """Create dates for the chat"""

    def __init__(self, bot):
        self.bot = bot
        self.dates_path = "data/dates/dates.json"
        self.dates = dataIO.load_json(self.dates_path)


    @commands.group(name="termin", pass_context=True)
    async def date(self, ctx):
        """ Verwaltet Termine fürs Team"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
    @date.command(name="aktivieren", pass_context=True)
    async def _activate(self, ctx):
        """Aktiviere die Terminverwaltung für diesen Server."""

        server = ctx.message.server
        if server.id not in self.dates:
            self.dates[server.id] = {}
            dataIO.save_json(self.dates_path, self.dates)

    @date.command(name="neu", pass_context=True)
    async def _new_date(self, ctx, date: str, time: str, note: str):
        """Erstelle einen neuen Termin."""

        newDate = (date, time, note)
        server = ctx.message.server
        self.dates[server.id] = {}
        self.dates[server.id][date] = {}
        self.dates[server.id][date][time] = note
        dataIO.save_json(self.dates_path, self.dates)
        self.dates = dataIO.load_json(self.dates_path)

    @date.command(name="liste", pass_context=True)
    async def _list_dates(self, ctx):
        """Listet alle Termine auf."""

        server = ctx.message.server
        dates = self.dates[server.id]
        embed = discord.Embed(title="Termine")
        for date in dates:
            header = self.dates[server.id][date]
            for time in date:
                datetext = "*" + self.dates[server.id][date][time] + "*"
                embed.add_field(name=header, value=datetext)
        await self.bot.say(embed=embed)



def check_folders():
    if not os.path.exists("data/dates"):
        print("Creating data/dates directory...")
        os.makedirs("data/dates")

def check_files():
    f = "data/dates/dates.json"
    if not dataIO.is_valid_json(f):
        print("Creating data/dates/dates.json...")
        dataIO.save_json(f, {})

def setup(bot):
    check_folders()
    check_files()
    n = Dates(bot)
    bot.add_cog(n)
