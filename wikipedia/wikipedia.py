import os
import aiohttp
import discord
from discord.ext import commands
from __main__ import send_cmd_help
from .utils.dataIO import dataIO


class Wikipedia:
    """
    The Wikipedia Cog
    """
    def __init__(self, bot):
        self.bot = bot
        self.settings_folder = "data/wikipedia"
        self.settings_path = self.settings_folder + "/settings.json"

        self.check_folders()
        self.check_files()

        self.settings = dataIO.load_json(self.settings_path)

    @commands.group(name="wikiconfig", pass_context=True)
    async def wikiconfig(self, ctx):
        """
        Configure wikipedia plugin
        """
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @wikiconfig.command(name="set", pass_context=True)
    @checks.is_owner()
    async def _set_wikiconfig(self, ctx, domain: str):
        """
        Set wikipedia domain and language
        """
        valid_domains = ['da', 'de', 'en', 'fr', 'hr', 'it', 'nl', 'ru', 'tr']

        if domain in valid_domains:
            self.settings['domain'] = domain
            dataIO.save_json(self.settings_path, self.settings)
            await self.bot.say("Your domain has been set.")
        else:
            await self.bot.say("Invalid domain. Please choose one of these domains " + str(valid_domains))


    @commands.command(pass_context=True, name='wikipedia', aliases=['wiki', 'w'])
    async def _wikipedia(self, context, *, query: str):
        """
        Get information from Wikipedia
        """
        try:
            domain = self.settings['domain']
            if domain is "":
                await self.bot.say("Please set your wikipedia domain.")
                return

            url = 'https://'+domain+'.wikipedia.org/w/api.php?'
            payload = {}
            payload['action'] = 'query'
            payload['format'] = 'json'
            payload['prop'] = 'extracts'
            payload['titles'] = ''.join(query).replace(' ', '_')
            payload['exsentences'] = '5'
            payload['redirects'] = '1'
            payload['explaintext'] = '1'
            headers = {'user-agent': 'Red-cog/1.0'}
            conn = aiohttp.TCPConnector(verify_ssl=False)
            session = aiohttp.ClientSession(connector=conn)
            async with session.get(url, params=payload, headers=headers) as r:
                result = await r.json()
            session.close()
            if '-1' not in result['query']['pages']:
                for page in result['query']['pages']:
                    title = result['query']['pages'][page]['title']
                    description = result['query']['pages'][page]['extract'].replace('\n', '\n\n')
                em = discord.Embed(title='Wikipedia: {}'.format(title), description='\a\n{}...\n\a'.format(description[:-3]), color=discord.Color.blue(), url='https://en.wikipedia.org/wiki/{}'.format(title.replace(' ', '_')))
                em.set_footer(text='Information provided by Wikimedia', icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Wikimedia-logo.png/600px-Wikimedia-logo.png')
                await self.bot.say(embed=em)
            else:
                message = 'I\'m sorry, I can\'t find {}'.format(''.join(query))
                await self.bot.say('```{}```'.format(message))
        except Exception as e:
            message = 'Something went terribly wrong! [{}]'.format(e)
            await self.bot.say('```{}```'.format(message))

    def check_folders(self):
        if not os.path.exists(self.settings_folder):
            print("Creating {} folder...".format(self.settings_folder))
            os.makedirs(self.settings_folder)

    def check_files(self):
        default = {'domain': ''}
        if not dataIO.is_valid_json(self.settings_path):
            print("Creating default wikipedia settings.json...")
            dataIO.save_json(self.settings_path, default)

def setup(bot):
    n = Wikipedia(bot)
    bot.add_cog(n)
