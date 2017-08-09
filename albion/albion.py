import discord
import asyncio
import aiohttp
import os
from discord.ext import commands
from .utils.dataIO import dataIO
from __main__ import send_cmd_help

class Albion:

    """Check Albion things"""

    def __init__(self, bot):
        self.bot = bot
        self.settings_path = "data/albion"
        self.settings_filepath = self.settings_path + "/" + "channels.json"
        self.settings = dataIO.load_json(self.settings_path+"/"+self.settings_filename)
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
            self.settings[server.id][channel.id] = self._check_online()
        dataIO.save_json(self.settings_filepath, self.settings)

    async def _check_online(self):
        url = "http://live.albiononline.com/status.txt"
        headers = {'user-agent': 'Tron-cog/1.0'}
        conn = aiohttp.TCPConnector(verify_ssl=False)
        session = aiohttp.ClientSession(connector=conn)
        async with session.get(url, headers=headers) as r:
            result = await r.json()
        session.close()
        if(result[status] == "online"):
            return True
        if(result[status] == "offline"):
            return False
        return False

    async def checkStatus(self):
        while True:
            await asyncio.sleep(360)
            server_online = self._check_online()
            for serverId in self.settings:
                for channel in self.settings[serverId]:
                    if channel != server_online and server_online == False:
                        await self.bot.send_message(channel, 'Albion Online Server ist offline!')
                    else:
                        await self.bot.send_message(channel, 'Albion Online Server ist wieder online!')

    def check_folders():
        if not os.path.exists(self.settings_path):
            print("Creating data/dates directory...")
            os.makedirs(self.settings_path)

    def check_files():
        f = "data/dates/dates.json"
        if not dataIO.is_valid_json(self.settings_filepath):
            print("Creating "+ self.settings_filepath +"...")
            dataIO.save_json(f, {})

def setup(bot):
    n = Albion(bot)
    n.check_folders()
    n.check_files()
    bot.add_cog(n)
