import discord
import asyncio
import aiohttp
import os
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help


settings_path = "data/albion"
settings_filepath = settings_path + "/" + "channels.json"

class Albion:

    """Check Albion things"""

    def __init__(self, bot):
        self.bot = bot
        self.settings_path = settings_path
        self.settings_filepath = settings_filepath
        try:
            self.settings = dataIO.load_json(self.settings_filepath)
        except:
            self.check_folders()
            self.check_files()
            self.settings = dataIO.load_json(self.settings_filepath)
        self.check_task = bot.loop.create_task(self.checkStatus())

    def __unload(self):
        self.check_task.cancel()

    @commands.group(name="albion", pass_context=True)
    async def albion(self, ctx):
        """ Verschiedene Dinge für Albion Online """
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @albion.command(name="statuscheck", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _set_statuscheck(self, ctx, status: str):
        """ Schaltet den Statuscheck für diesen Channel ein. """
        server = ctx.message.server
        channel = ctx.message.channel
        if(status == "an"):
            if server.id not in self.settings:
                self.settings[server.id] = {}
            if channel.id not in self.settings[server.id]:
                self.settings[server.id][channel.id] = {}
            status = await self._check_online()
            self.settings[server.id][channel.id] = status
        if(status == "aus"):
            if channel.id in self.settings[server.id]:
                del self.settings[server.id][channel.id]
        dataIO.save_json(self.settings_filepath, self.settings)
        self.settings = dataIO.load_json(self.settings_filepath)

    @albion.command(name="status", pass_context=True, aliases=['astat'])
    async def _get_status(self, ctx):
        """ Fragt den momentanen Status der Server ab. """
        status = await self._check_online()
        if status == "offline":
            await self.bot.say(':no_entry: Albion Online ist offline! :no_entry:')
        if status == "online":
            await self.bot.say('Albion Online ist online! :crossed_swords:')

    async def _check_online(self):
        url = "https://api.albionstatus.com/current/"
        headers = {'user-agent': 'Tron-cog/1.0'}
        conn = aiohttp.TCPConnector(verify_ssl=False)
        session = aiohttp.ClientSession(connector=conn)
        async with session.get(url, headers=headers) as r:
            result = await r.json()
        session.close()
        if "offline" in result[0]['current_status']:
            return "offline"
        if "online" in result[0]['current_status']:
            return "online"

    async def checkStatus(self):
        print("Status Check Cronjob started...")
        while True:
            await asyncio.sleep(300)
            server_status = await self._check_online()
            for serverId in self.settings:
                for channelId in self.settings[serverId]:
                    if self.settings[serverId][channelId] == server_status:
                        pass
                    if self.settings[serverId][channelId] != server_status and server_status == "online":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), ':hammer_pick: :regional_indicator_a:lbion ist :regional_indicator_o:nline! :crossed_swords:')
                    if self.settings[serverId][channelId] != server_status and server_status == "offline":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), ':no_entry: :regional_indicator_a:lbion ist :o2:ffline! :no_entry:')
                    if self.settings[serverId][channelId] != server_status and server_status == "starting":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), ':airplane_departure: :regional_indicator_a:lbion Server sind am starten! :airplane_departure: ')
                    if self.settings[serverId][channelId] != server_status and server_status == "unknown":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), ':scream: :regional_indicator_a:lbions Zustand ist unklar! Möglicherweise ist gerade Wartung im Gange. :thinking:')

def check_folders():
    if not os.path.exists(settings_path):
        print("Creating data/dates directory...")
        os.makedirs(settings_path)

def check_files():
    if not dataIO.is_valid_json(settings_filepath):
        print("Creating "+ settings_filepath +"...")
        dataIO.save_json(settings_filepath, {})

def setup(bot):
    check_folders()
    check_files()
    n = Albion(bot)
    bot.add_cog(n)
