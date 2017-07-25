import discord
import asyncio
import re
import os
import datetime
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

    @date.command(name="neu", pass_context=True)
    async def _new_date(self, ctx, date: str, time: str, note: str):
        """Erstelle einen neuen Termin."""

        if not self.checkDateTime(date, time):
            print("checking datetime")
            await self.bot.say("Bitte ein korrektes Datum und eine korrekte Uhrzeit angeben.")
            return

        newDate = (date, time, note)
        server = ctx.message.server
        if server.id not in self.dates:
            self.dates[server.id] = {}
        if date not in self.dates[server.id]:
            self.dates[server.id][date] = {}
        self.dates[server.id][date][time] = note
        dataIO.save_json(self.dates_path, self.dates)
        self.dates = dataIO.load_json(self.dates_path)
        await self.bot.say("Termin angelegt.")

    @date.command(name="liste", pass_context=True)
    async def _list_dates(self, ctx):
        """Listet alle Termine auf."""

        server = ctx.message.server
        dates = self.dates[server.id]
        embed = discord.Embed(title="Termine", color = 0x00c9f4)
        datetext = ""
        for date in dates:
            header = date
            for time in self.dates[server.id][date]:
                datetext += "*" + time + "* - " + self.dates[server.id][date][time] + "\n"
            embed.add_field(name=header, value=datetext)
            datetext = ""
        await self.bot.say(embed=embed)

    @date.command(name="löschen", pass_context=True)
    async def _del_date(self, ctx, date: str, time: str):
        """Lösche einen Termin mit angegebenem Datum und Uhrzeit."""

        if not self.checkDateTime(date, time):
            await self.bot.say("Bitte ein korrektes Datum und eine korrekte Uhrzeit angeben.")
            return

        server = ctx.message.server
        if server.id in self.dates:
            if date in self.dates[server.id]:
                if time in self.dates[server.id][date]:
                    del self.dates[server.id][date][time]
                    await self.bot.say("Termin gelöscht.")

        if not self.dates[server.id][date]:
            del self.dates[server.id][date]

        dataIO.save_json(self.dates_path, self.dates)
        self.dates = dataIO.load_json(self.dates_path)

    async def checkDateTime(self, date, time):
        try:
            datetimestring = date + " " + time
            print(datetimestring)
            datetime.datetime.strptime(datetimestring, '%d.%m.%y %H:%M')
            return True
        except ValueError:
            return False

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
