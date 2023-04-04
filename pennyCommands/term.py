import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal,get_args

class TerminateCommands(commands.Cog):

    MANAGER_BOT_CHANNEL = 958744862583304233
    OFF_TOPIC_CHANNEL = 933576125614010419
    
    MOD_LOG_CHANNEL = 933202716359028796

    MANAGER_ROLE_ID = [920698657160982578, 958433853834420265]
    FORMER_STAFF_ROLE_ID = 942508946516746330

    TERM_LIST = Literal['Voluntary', 'Involuntary - Kick']
    
    VALID_TERM_STATUS = list(get_args(TERM_LIST))

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        description="Update memebers roles or kicks based after termination",
    )
    @app_commands.describe(status='What type of termination occured', emp="Employee to term in Discord", reason="Reason for termination (optional)")
    @commands.has_any_role(*MANAGER_ROLE_ID)
    async def term(self, ctx, status: TERM_LIST, emp: discord.Member, *, reason="No longer employed"): 
        if not (ctx.channel.id == self.MANAGER_BOT_CHANNEL): 
            await ctx.send("You posted in the wrong channel! For the command to be valid, you must use it in the <#" + str(self.MANAGER_BOT_CHANNEL) + "> channel.", ephemeral=True)
            return

        if status in self.VALID_TERM_STATUS:
            #valid termstatus provided
            pass
        else:
            await ctx.send("The term status provided seems to be invalid. Please use either 'voluntary' or 'involuntary' as the term status.", ephemeral=True)
            return


        if status == "Voluntary":
            formStaffRole = ctx.guild.get_role(self.FORMER_STAFF_ROLE_ID)
            await emp.edit(roles=[formStaffRole]) # Replaces all current roles with roles in list
            await ctx.send("**" + str(emp.nick) + " (" + str(emp.name) + ")** moved to Former Staff role. \nReason: " + str(reason), ephemeral=False)

            notifChn = self.bot.get_channel(self.OFF_TOPIC_CHANNEL)
            await notifChn.send("<@" + str(emp.id) + "> sad to see you go. Good luck on your future endeavours and any opportunities that come your way!")
        else:
            await ctx.send("**" + str(emp.nick) + " (" + str(emp.name) + ")** Termed and Kicked from server. \nReason: " + str(reason), ephemeral=False)
            await emp.kick(reason=str(reason))

            #Log Kick action in ModLog
            modLogChan = self.bot.get_channel(self.MOD_LOG_CHANNEL)
            kickEmbed = discord.Embed(title=f"Kicked {emp.nick}!", description=f"**Username:** {emp.name}#{emp.discriminator}\n**Reason:** {reason}\nBy: {ctx.author.mention}")

            await modLogChan.send(embed=kickEmbed)

    @term.error
    async def term_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send('The member specified cannot be found! If the username has a space in the name, make sure to put entire username in quotation marks.', ephemeral=True)


        

async def setup(bot): # Must have a setup function
    await bot.add_cog(TerminateCommands(bot)) # Add the class to the cog.