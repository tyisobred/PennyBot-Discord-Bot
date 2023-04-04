import discord
from discord.ext import commands

class UpdateTree(commands.Cog):

    AUTHORIZED_USR = [920696601742295040]

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="MANAGERS ONLY",
        brief="MANAGERS ONLY"
    )
    async def updatetree(self, ctx): 
        if not (ctx.message.author.id in self.AUTHORIZED_USR): 
            await ctx.send("This command can only be used by authorized users...")
            return
        await self.bot.tree.sync()
        await ctx.send("Tree Updated!")

async def setup(bot): # Must have a setup function
    await bot.add_cog(UpdateTree(bot)) # Add the class to the cog.