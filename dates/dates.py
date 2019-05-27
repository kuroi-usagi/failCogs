import discord
import asyncio
import re
import os
import datetime
from discord.ext import commands
from redbot.utils.dataIO import dataIO
from __main__ import send_cmd_help

class Dates:

    """Create dates for the chat"""

    def __init__(self, bot):
        self.bot = bot
        self.dates_path = "data/dates/dates.json"
        self.dates = dataIO.load_json(self.dates_path)
        self.cleanup_task = bot.loop.create_task(self.cleanup())

    def __unload(self):
        self.cleanup_task.cancel()

    @commands.group(name="termin", pass_context=True)
    async def date(self, ctx):
        """ Verwaltet Termine fürs Team"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @date.command(name="neu", pass_context=True)
    async def _new_date(self, ctx, date: str, time: str, note: str):
        """Erstelle einen neuen Termin.
        Format: dd.mm.yy hh:mm Beschreibung"""

        if not self.checkDateTime(date, time):
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
        if not server.id in self.dates:
            await self.bot.say("Es wurden bisher keine Termine für diesen Server angelegt.")
            return
            
        embed = discord.Embed(title="Termine", color = 0x00c9f4)
        datetext = ""
        for date in self.dates[server.id]:
            header = date
            for time in self.dates[server.id][date]:
                datetext += "*" + time + "* - " + self.dates[server.id][date][time] + "\n"
            embed.add_field(name=header, value=datetext)
            datetext = ""
        await self.bot.say(embed=embed)

    @date.command(name="löschen", pass_context=True)
    async def _del_date(self, ctx, date: str, time: str):
        """Lösche einen Termin mit angegebenem Datum und Uhrzeit.
        Format: dd.mm.yy hh:mm"""

        if not self.checkDateTime(date, time):
            await self.bot.say("Bitte ein korrektes Datum und eine korrekte Uhrzeit angeben.")
            return

        server = ctx.message.server
        if await self._delete_date(server.id, date, time):
            await self.bot.say("Termin gelöscht.")

    async def _delete_date(self,serverId, date, time):
        deletedState = False
        try:
            if serverId in self.dates:
                if date in self.dates[serverId]:
                    if time in self.dates[serverId][date]:
                        del self.dates[serverId][date][time]
                        deletedState = True
            if not self.dates[serverId][date]:
                del self.dates[serverId][date]
        except:
            print("error when deleting stuff")
        else:
            dataIO.save_json(self.dates_path, self.dates)
            self.dates = dataIO.load_json(self.dates_path)

        return deletedState

    async def cleanup(self):
        while True:
            await asyncio.sleep(360)
            delete_dates = []
            for serverId in self.dates:
                for date in self.dates[serverId]:
                    for time in self.dates[serverId][date]:
                        date_time_string = date + " " + time
                        date_datetime = datetime.datetime.strptime(date_time_string, '%d.%m.%y %H:%M')
                        if datetime.datetime.now() > date_datetime:
                            delete_dates.append((serverId, date, time))
            for deleteItems in delete_dates:
                await self._delete_date(deleteItems[0], deleteItems[1], deleteItems[2])

    def checkDateTime(self, date, time):
        try:
            datetimestring = date + " " + time
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
