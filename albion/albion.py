import discord
import asyncio
import aiohttp
import os
from discord.ext import commands
from .utils.dataIO import dataIO
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
    async def _set_statuscheck(self, ctx, status: str):
        """ Schaltet den Statuscheck für diesen Channel ein. """
        if(status == "an"):
            server = ctx.message.server
            channel = ctx.message.channel
            if server.id not in self.settings:
                self.settings[server.id] = {}
            if channel.id not in self.settings[server.id]:
                self.settings[server.id][channel.id] = {}
            status = await self._check_online()
            self.settings[server.id][channel.id] = status
            print(status)
        dataIO.save_json(self.settings_filepath, self.settings)
        self.settings = dataIO.load_json(self.settings_filepath)

    async def _check_online(self):
        url = "http://live.albiononline.com/status.txt"
        headers = {'user-agent': 'Tron-cog/1.0'}
        conn = aiohttp.TCPConnector(verify_ssl=False)
        session = aiohttp.ClientSession(connector=conn)
        async with session.get(url, headers=headers) as r:
            result = await r.text()
        session.close()
        if "offline" in result:
            return "offline"
        if "online" in result:
            return "online"

    async def checkStatus(self):
        print("Status Check Cronjob started...")
        while True:
            await asyncio.sleep(60)
            print("scanning server")
            server_status = await self._check_online()
            for serverId in self.settings:
                for channelId in self.settings[serverId]:
                    print(self.settings[serverId][channelId])
                    print(server_status)
                    print(self.settings[serverId][channelId] == server_status)
                    if self.settings[serverId][channelId] == server_status:
                        pass
                    if self.settings[serverId][channelId] != server_status and server_status == "online":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), 'Albion Online Server ist online! :crossed_swords:')
                    if self.settings[serverId][channelId] != server_status and server_status == "offline":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), ':no_entry: Albion Online Server ist offline! :no_entry:')

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
