import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os
from .utils.chat_formatting import *

class GamingAccount:
    """The GamingAccount Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.profile = "data/gamingaccount/accounts.json"
        self.nerdie = dataIO.load_json(self.profile)
    
    @commands.command(name="signup", pass_context=True, invoke_without_command=True, no_pm=True)
    async def _reg(self, ctx):
        """Melde dich an um deinen Account einzustellen"""

        server = ctx.message.server
        user = ctx.message.author
        
        if server.id not in self.nerdie:
            self.nerdie[server.id] = {}
        else:
            pass

        if user.id not in self.nerdie[server.id]:
            self.nerdie[server.id][user.id] = {}
            dataIO.save_json(self.profile, self.nerdie)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Glückwunsch!:sparkles:", value="Du hast einen Account angelegt für **{}**, {}.".format(server, user.mention))
            await self.bot.say(embed=data)
        else: 
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:Warnung:",value="Sieht so aus als hättest du schon einen Account, {}.".format(user.mention))
            await self.bot.say(embed=data)
        
    
    @commands.command(name="account", pass_context=True, invoke_without_command=True, no_pm=True)
    async def _acc(self, ctx, user : discord.Member=None):
        """Dein/ein anderer Account"""
                    
        server = ctx.message.server
        
        if server.id not in self.nerdie:
            self.nerdie[server.id] = {}
        else:
            pass

        if not user:
            user = ctx.message.author
            if user.id in self.nerdie[server.id]:
                data = discord.Embed(description="{}".format(server), colour=user.colour)
                if "PSN" in self.nerdie[server.id][user.id]:
                    age = self.nerdie[server.id][user.id]["PSN"]
                    data.add_field(name="PSN:", value=psn)
                else:
                    pass
                if user.avatar_url:
                    name = str(user)
                    name = " ~ ".join((name, user.nick)) if user.nick else name
                    data.set_author(name=name, url=user.avatar_url)
                    data.set_thumbnail(url=user.avatar_url)
                else:
                    data.set_author(name=user.name)

                await self.bot.say(embed=data)
            else:
                prefix = ctx.prefix
                data = discord.Embed(colour=user.colour)
                data.add_field(name="Error:Warnung:",value="Du brauchst einen Account um das nutzen zu können. \n\nUm einen anzulegen sage einfach `{}signup`.".format(prefix))
                await self.bot.say(embed=data)
        else:
            server = ctx.message.server
            if user.id in self.nerdie[server.id]:
                data = discord.Embed(description="{}".format(server), colour=user.colour)
                if "PSN" in self.nerdie[server.id][user.id]:
                    town = self.nerdie[server.id][user.id]["PSN"]
                    data.add_field(name="PSN", value=town)
                else:
                    pass
                if user.avatar_url:
                    name = str(user)
                    name = " ~ ".join((name, user.nick)) if user.nick else name
                    data.set_author(name=name, url=user.avatar_url)
                    data.set_thumbnail(url=user.avatar_url)
                else:
                    data.set_author(name=user.name)

                await self.bot.say(embed=data)
            else:
                data = discord.Embed(colour=user.colour)
                data.add_field(name="Error:Warnung:",value="{} hat keinen Account.".format(user.mention))
                await self.bot.say(embed=data)

    @commands.group(name="update", pass_context=True, invoke_without_command=True, no_pm=True)
    async def update(self, ctx):
        """Update deine Infos"""
        await send_cmd_help(ctx)

    @update.command(pass_context=True, no_pm=True)
    async def psn(self, ctx, *, age):
        """Wie lautet deine PSN?"""
        
        server = ctx.message.server
        user = ctx.message.author
        prefix = ctx.prefix

        if server.id not in self.nerdie:
            self.nerdie[server.id] = {}
        else:
            pass

        if user.id not in self.nerdie[server.id]:
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Error:Warnung:",value="Du brauchst einen Account um das nutzen zu können. \n\nUm einen anzulegen sage einfach `{}signup`.".format(prefix))
            await self.bot.say(embed=data)
        else:
            self.nerdie[server.id][user.id].update({"PSN" : age})
            dataIO.save_json(self.profile, self.nerdie)
            data = discord.Embed(colour=user.colour)
            data.add_field(name="Glückwunsch!:sparkles:",value="Deine PSN ist jetzt {}".format(age))
            await self.bot.say(embed=data)

def check_folder():
    if not os.path.exists("data/gamingaccount"):
        print("Creating data/account folder...")
        os.makedirs("data/gamingaccount")

def check_file():
    data = {}
    f = "data/gamingaccount/accounts.json"
    if not dataIO.is_valid_json(f):
        print("I'm creating the file, so relax bruh.")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(GamingAccount(bot))