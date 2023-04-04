import discord
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions, has_any_role
from discord import Member
from discord import Embed,File
from typing import Optional
from random import choice
from asyncio import TimeoutError, sleep

class GiveawayCommands(Cog, name="Giveaway Commands", description="Manager Use Only Commands. These are a group of commands used to manage and create giveaways."):
    MANAGER_ROLE_ID = [920698657160982578, 958433853834420265]

    def __init__(self,bot):
        self.bot = bot
        self.cancelled = False
        self.numGiveaways = 0
        self.giveawayName = ""
        self.prize = ""


    @command(
        # ADDS THIS VALUE TO THE $HELP PING MESSAGE.
        help="Creates a giveaway in the specified channel that automatically chooses a winner after the time specified. You have 25 seconds to answer all three questions.",
        # ADDS THIS VALUE TO THE $HELP MESSAGE.
        brief="Creates a Giveaway for the speficied duration in the specified channel."
    )
    @has_any_role(*MANAGER_ROLE_ID)
    async def giveaway_create(self, ctx):
        if self.numGiveaways > 0:
            embed = Embed(title="Giveaway Already in Progress",
                      description="A Giveaway is already in progress. To avoid issues, please wait until the current giveaway is completed.",
                      color=ctx.author.color)
            await ctx.send(embed=embed)
            return
        else:
            self.numGiveaways = self.numGiveaways + 1
        #Ask Questions
        embed = Embed(title="Giveaway Setup Process",
                      description="Time for a new Giveaway. Answer the following questions in 25 seconds each for the Giveaway",
                      color=ctx.author.color)
        await ctx.send(embed=embed)
        questions=["In Which channel do you want to host the giveaway?",
                   "For How long should the Giveaway be hosted? Type a number followed by (s|m|h|d)",
                   "What will the winner recieve?", 
                   "What is the name of this giveaway?"]
        answers = []
        #Check Author
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i+1}",
                          description=question)
            await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for('message', timeout=25, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the questions in Time")
                return
            answers.append(message.content)
        #Check if Channel Id is valid
        try:
            channel_id = int(answers[0][2:-1])
        except:
            await ctx.send(f"The Channel provided was wrong. The channel should be in the format of {ctx.channel.mention}")
            return

        channel = self.bot.get_channel(channel_id)
        time = convert(answers[1])
        self.giveawayName = str(answers[3])
        #Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong")
            return
        elif time == -2:
            await ctx.send("The Time was not conventional number")
            return
        self.prize = str(answers[2])

        await ctx.send(f"This giveaway will be hosted in {channel.mention} and a winner will automaticaly be choosen in {answers[1]}")
        embed = Embed(title=self.giveawayName,
                    description=f"Enter to win the following: {self.prize}",
                    colour=0x00FFFF)
        embed.add_field(name="Hosted By:", value=ctx.author.mention)
        embed.set_footer(text=f"Giveway ends in {answers[1]} from now")
        newMsg = await channel.send(embed=embed)
        await newMsg.add_reaction("🎉")
        #Check if Giveaway Cancelled
        self.cancelled = False
        await sleep(time)
        if not self.cancelled:
            myMsg = await channel.fetch_message(newMsg.id)

            users = await myMsg.reactions[0].users().flatten()
            users.pop(users.index(self.bot.user))
            #Check if User list is not empty
            if len(users) <= 0:
                emptyEmbed = Embed(title=self.giveawayName,
                                   description=f"Giveaway for the following is over: {self.prize}")
                emptyEmbed.add_field(name="Hosted By:", value=ctx.author.mention)
                emptyEmbed.set_footer(text="No one won the Giveaway")
                await myMsg.edit(embed=emptyEmbed)
                self.numGiveaways = 0
                return
            if len(users) > 0:
                winner = choice(users)
                winnerEmbed = Embed(title=self.giveawayName,
                                    description=f"Giveaway for the following is over: {self.prize}",
                                    colour=0x00FFFF)
                winnerEmbed.add_field(name=f"Congratulations On Winning a {self.prize}", value=winner.mention)
                # winnerEmbed.set_image(url="https://firebasestorage.googleapis.com/v0/b/sociality-a732c.appspot.com/o/Loli.png?alt=media&token=ab5c8924-9a14-40a9-97b8-dba68b69195d")
                await myMsg.edit(embed=winnerEmbed)
                await myMsg.reply(f"Congratulations {winner.mention} on winning the giveaway!")
                self.numGiveaways = 0
                return

    # @create_giveaway.error
    # async def create_giveaway_error(self, ctx, exc):
    #     if isinstance(exc, MissingPermissions):
    #         await ctx.send("You are not allowed to create Giveaways")
        

    @command(
        # ADDS THIS VALUE TO THE $HELP PING MESSAGE.
        help="Chooses a new winner for the giveaway specified. Must use the giveaway message ID and the channel. ",
        # ADDS THIS VALUE TO THE $HELP MESSAGE.
        brief="Chooses a a new winner for a giveaway."
    )
    @has_any_role(*MANAGER_ROLE_ID)
    async def giveaway_reroll(self, ctx, channel : discord.TextChannel, id_: int):
        try:
            msg = await channel.fetch_message(id_)
        except:
            await ctx.send("The channel or ID mentioned was incorrect")
        users = await msg.reactions[0].users().flatten()
        if len(users) <= 0:
            emptyEmbed = Embed(title=self.giveawayName,
                                description=f"Giveaway for the following is over: {self.prize}")
            emptyEmbed.add_field(name="Hosted By:", value=ctx.author.mention)
            emptyEmbed.set_footer(text="No one won the Giveaway")
            await msg.edit(embed=emptyEmbed)
            return
        if len(users) > 0:
            winner = choice(users)
            winnerEmbed = Embed(title=self.giveawayName,
                                description=f"Giveaway for the following is over: {self.prize}",
                                colour=0x00FFFF)
            winnerEmbed.add_field(name=f"Congratulations On Winning a {self.prize}", value=winner.mention)
            # winnerEmbed.set_image(url="https://firebasestorage.googleapis.com/v0/b/sociality-a732c.appspot.com/o/Loli.png?alt=media&token=ab5c8924-9a14-40a9-97b8-dba68b69195d")
            await msg.edit(embed=winnerEmbed)
            await msg.reply(f"Congratulations {winner.mention} on winning the giveaway!")
            return

                # users.pop(users.index(self.bot.user))
                # winner = choice(users)
                # await channel.send(f"Congratulations {winner.mention} on winning the Giveaway")

    @command(
        # ADDS THIS VALUE TO THE $HELP PING MESSAGE.
        help="Cancels a giveaway with the specified channel and message ID.",
        # ADDS THIS VALUE TO THE $HELP MESSAGE.
        brief="Cancel a giveaway"
    )
    @has_any_role(*MANAGER_ROLE_ID)
    async def giveaway_stop(self, ctx, channel : discord.TextChannel, id_: int):
        try:
            msg = await channel.fetch_message(id_)
            newEmbed = Embed(title="Giveaway Cancelled", description="The giveaway has been cancelled!!")
            #Set Giveaway cancelled
            self.cancelled = True
            await msg.edit(embed=newEmbed) 
        except:
            embed = Embed(title="Failure!", description="Cannot cancel Giveaway")
            await ctx.send(emebed=embed)


async def setup(bot):
    await bot.add_cog(GiveawayCommands(bot))

def convert(time):
    pos = ["s","m","h","d"]
    time_dict = {"s": 1,"m": 60,"h": 3600,"d": 24*3600 }
    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        timeVal = int(time[:-1])
    except:
        return -2

    return timeVal*time_dict[unit]