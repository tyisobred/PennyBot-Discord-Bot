import asyncio
import logging
import logging.handlers
import os
import time
from datetime import datetime, timedelta

from typing import List, Optional

import discord
from discord.ext import commands

# IMPORT THE COMMANDS.
from pennyCommands import *
from pennyCommands.verification import PersistentView,PersistentViewPosistion,PersistentViewRules

import feedparser
import random


class PennyBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:

        # here, we are loading extensions prior to sync to ensure we are syncing interactions defined in those extensions.

        for extension in self.initial_extensions:
            await self.load_extension(extension)
            print("%s has loaded." % extension)
        self.add_view(PersistentView())
        self.add_view(PersistentViewRules())
        #self.add_view(PersistentViewPosistion())


        self.bg_task = self.loop.create_task(self.loadTrailerFeed())

        # In overriding setup hook,
        # we can do things that require a bot prior to starting to process events from the websocket.
        # In this case, we are using this to ensure that once we are connected, we sync for the testing guild.
        # You should not do this for every guild or for global sync, those should only be synced when changes happen.
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)

        # This would also be a good place to connect to our database and
        # load anything that should be in memory prior to handling events.

    async def on_ready(self):
        #await bot.tree.sync()
        # CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
        guild_count = 0

        # LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
        for guild in self.guilds:
            # PRINT THE SERVER'S ID AND NAME.
            print(f"- {guild.id} (name: {guild.name})")

            # INCREMENTS THE GUILD COUNTER.
            guild_count = guild_count + 1

        # PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
        print("PennyBot is in " + str(guild_count) + " guilds.")
        print("PennyBot is Online")

    async def on_message(self,message):
        CMD_ONLY_CHANNELS = [984544002068058122,993745411837796352]
        if not message.author.bot and message.channel.id in CMD_ONLY_CHANNELS:
            if len(message.attachments) > 0 or not message.content[0] == "!":
                # Non-CMD in CMD only channel. DM user that the message was removed and to use a command.
                try:
                    await message.author.send("You recently sent the message below to the (<#" + str(message.channel.id) + ">) channel which is **restricted to __Commands Only__**! This message has been permanently deleted and is no longer visible to anyone on the server. Please either place your message in a different channel, or use a command. \n\nUse the `!help` command to see the available commands.\n\n `" + message.content + "`")
                except:
                    await message.channel.send("<@" + str(message.author.id) + "> This channel is only for messages from bots and Commands. Any non-command messages are automatically deleted permanently. Please use a different channel")
                await message.delete()
            else:
                # INCLUDES THE COMMANDS FOR THE BOT. WITHOUT THIS LINE, YOU CANNOT TRIGGER YOUR COMMANDS.
                await self.process_commands(message)
        else:
            # INCLUDES THE COMMANDS FOR THE BOT. WITHOUT THIS LINE, YOU CANNOT TRIGGER YOUR COMMANDS.
            await self.process_commands(message)


    async def on_command_error(self, ctx, error):
        LOG_CHANNELS = 1044863892540629034
        if isinstance(error, commands.BadLiteralArgument):
            await ctx.reply("Wrong volue entered. Please use one of the following: " + str(getattr(error,"literals")), ephemeral=True)
            await self.get_channel(LOG_CHANNELS).send("BadLiteralArgument Error using command - " + str(ctx.command) + "\nUser: " + str(ctx.author) + "\nMessage: " + str(ctx.message.content))
        elif isinstance(error, commands.HybridCommandError):
            await ctx.reply("Slash command seems to have failed. This is likely due to the server being slow... Please try the command again as soon as possible!", ephemeral=True)
            await self.get_channel(LOG_CHANNELS).send("HybridCommandError Error using command - " + str(ctx.command) + "\nUser: " + str(ctx.author) + "\nMessage: " + str(ctx.message.content))
        elif isinstance(error, commands.MissingAnyRole):
            await ctx.reply("You are snooping in areas you shouldn't. Please do not use manager only commands.", ephemeral=True)
            await self.get_channel(LOG_CHANNELS).send("MissingAnyRole Error using command - " + str(ctx.command) + "\nUser: " + str(ctx.author) + "\nMessage: " + str(ctx.message.content))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Command missing something. Try running `!help [CMD]` to see what the syntax of the command is.", ephemeral=True)
            await self.get_channel(LOG_CHANNELS).send("MissingRequiredArgument Error using command - " + str(ctx.command) + "\nUser: " + str(ctx.author) + "\nMessage: " + str(ctx.message.content))
        raise error

    async def loadTrailerFeed(self):
        await self.wait_until_ready()
        channel = self.get_channel(933575658964131940)  # channel ID goes here
        while not self.is_closed():
            logging.info("ComingSoon Movies: Start of Run")
            position=0
            oneHour = 3600
            freqHour = oneHour * 4
            nextIt = oneHour * 24

            while int(datetime.now().strftime("%H")) < 8 or int(datetime.now().strftime("%H")) >= 20:
                logging.info("ComingSoon Movies: Delaying run until morning time")
                await asyncio.sleep(oneHour) # Delay new cycle until morning time to avoid a cycle running at night time
                break


            NewsFeed = feedparser.parse("https://www.fandango.com/rss/comingsoonmovies.rss")
            logging.info("ComingSoon Movies: Fetched new movies List")
            lenDic = len(NewsFeed)

            with open('comingSoonLog.txt', 'r') as f:
                prevMoviesList = f.read().split("###;###")

            curMoviesList = []

            for entry in NewsFeed.entries:
                position += 1
            #    print (key, value) 
                if entry.title in prevMoviesList:
                    curMoviesList.append(entry.title)
                    continue
                
                #Add cur movie to new database list
                curMoviesList.append(entry.title)
                with open('comingSoonLog.txt', 'w') as f:
                    f.write("###;###".join(curMoviesList))

                # Was this movie published within the last 24 hours?
                if datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z') > (datetime.now() - timedelta(hours = 24)):

                    summary = entry.summary[entry.summary.find("</a>")+5:entry.summary.find("</p><p><a")]
                    summary = summary.replace("</p><p>", "\n\n")

                    poster = entry.links[1]['href']
                    movieURL = entry.links[0]['href']
                    title = entry.title
                    trailer = entry.fan_trailer


                    movieEmbed = discord.Embed(title=title, url=movieURL, description=summary, color=0xdd74f2)
                    movieEmbed.set_thumbnail(url=poster)
                    movieEmbed.add_field(name="Watch the trailer for " + str(title) + " below", value=trailer, inline=False)
                    await channel.send(embed=movieEmbed)
                else:
                    continue

                if position <= lenDic-2:
                    nextIt = freqHour + random.randint(-1800, 1800)
                    await asyncio.sleep(nextIt)  # task runs every 30-90 minutes
                else:
                    break

                while int(datetime.now().strftime("%H")) < 8 or int(datetime.now().strftime("%H")) >= 20:
                    logging.info("ComingSoon Movies: Delaying Cycle until morning time")
                    await asyncio.sleep(oneHour) # Delay new cycle until morning time to avoid a cycle running at night time
                    break

            logging.info("ComingSoon Movies: End of run. Next run starts in 24 hours.")
            await asyncio.sleep(oneHour * 24) #run next update cycle in 24 hours.


async def main():

    # When taking over how the bot process is run, you become responsible for a few additional things.

    # 1. logging

    # for this example, we're going to set up a rotating file logger.
    # for more info on setting up logging,
    # see https://discordpy.readthedocs.io/en/latest/logging.html and https://docs.python.org/3/howto/logging.html

    #logger = logging.getLogger('discord')
    #logger.setLevel(logging.INFO)

    

    handler = logging.handlers.RotatingFileHandler(
        filename='discordError.log',
        encoding='utf-8',
        maxBytes=1024 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )

    discord.utils.setup_logging(handler=handler, level=logging.INFO, root=True)

    # One of the reasons to take over more of the process though
    # is to ensure use with other libraries or tools which also require their own cleanup.

    # Here we have a web client and a database pool, both of which do cleanup at exit.
    # We also have our bot, which depends on both of these.


    exts = ['pennyCommands.late', 'pennyCommands.giveaway', 'pennyCommands.verification', 'pennyCommands.term', 'pennyCommands.planogram', 'pennyCommands.shiftswaps', 'pennyCommands.trivia', 'pennyCommands.updatetree']
    intents = discord.Intents.all()
    async with PennyBot(command_prefix="!", intents=intents, initial_extensions=exts, testing_guild_id=992149593930338455) as bot:
        # GRAB THE API TOKEN FROM THE FILE.
        Secret = open("token.txt", 'r')
        DISCORD_TOKEN = Secret.read()
        #await bot.start(os.getenv('TOKEN', ''))
        await bot.start(DISCORD_TOKEN)



# For most use cases, after defining what needs to run, we can just tell asyncio to run it:
asyncio.run(main())

























