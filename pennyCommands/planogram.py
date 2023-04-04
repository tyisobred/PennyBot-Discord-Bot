import discord
from discord import app_commands
from discord.ext import commands
import requests
import imghdr
import os
from time import gmtime, strftime, sleep
import glob
from typing import Literal,get_args

class PlanogramCommands(commands.Cog):

    UPDATE_PG_LIST = Literal['candy', 'drinks-lg', 'drinks-sm', 'chips', 'nestle', 'food', 'popcorn', 'mars']
    
    PLANOGRAM_LIST = list(get_args(UPDATE_PG_LIST))


    MANAGER_ROLE_ID = [920698657160982578, 958433853834420265]
    CON_CHANNEL = 936768858570784789
    CON_ROLE_ID = 933198816218337301

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        description="View the Planogram for the choosen item.",
    )
    @app_commands.describe(planogram='The planogram type that is you wish to view')
    async def planogram(self, ctx, planogram: UPDATE_PG_LIST):
        if not (ctx.channel.id == self.CON_CHANNEL): 
            await ctx.send("This command can only be used in the <#" + str(self.CON_CHANNEL) + "> channel.", ephemeral=True)
            return

        if not planogram in self.PLANOGRAM_LIST:
            await ctx.send("The Planogram you specified does not exist. Please choose from the following: " + ",".join(self.PLANOGRAM_LIST), ephemeral=True)
            return

        #await ctx.defer(ephemeral=True)

        filename = None
        for planogramFilename in glob.glob("planogramImg/" + str(planogram) + "_*"):
            asOfDate = planogramFilename.split("_")[1]
            filename = planogramFilename

        if filename:
            await ctx.send(str(planogram).title() + " Planogram as of: " + str(asOfDate) , file=discord.File(filename), ephemeral=False)
        else:
            await ctx.send("It seems there are no planogram pictures for the " + str(planogram).title() + " Planogram. Please notify the Concession Manager of this!", ephemeral=True)




    @commands.hybrid_command(
        description="Update the planogram images. Must use one of the planograms available in Planogram command.",
    )
    @app_commands.describe(planogram='The planogram type that is being updated', img="A JPG image of the new planogram.")
    @commands.has_any_role(*MANAGER_ROLE_ID)
    async def updateplanogram(self, ctx, planogram: UPDATE_PG_LIST, img: discord.Attachment): 
        if not (ctx.channel.id == self.CON_CHANNEL): 
            await ctx.send("This command can only be used in the <#" + str(self.CON_CHANNEL) + "> channel.", ephemeral=True)
            return
        elif not str(planogram) in self.PLANOGRAM_LIST:
            await ctx.send("The planogram you are trying to update does not seem to exist. Please use one of the following (case sensitive): " + ",".join(self.PLANOGRAM_LIST),ephemeral=True)
            return
        elif os.path.splitext(img.filename)[1] != ".jpg":
            await ctx.send("At this time, this command only accepts jpg image files. Please upload a jpg file or convert the file to a jpg.", ephemeral=True)
            return
        else:
            pass
        
        await ctx.defer(ephemeral=True)

        filename = str(planogram) + '_{0}'.format(strftime("%m-%d-%Y_%H_%M_%S", gmtime()))
        
        try:
            #remove old planogram image first before uploading new
            for oldfilename in glob.glob("planogramImg/" + str(planogram) + "_*"):
                os.remove(oldfilename)
            await img.save(f'planogramImg/{filename}.jpg')

            await ctx.send(str(planogram) + " Planogram Image updated successfully!",ephemeral=True)

            planogramUpdatePost = self.bot.get_channel(self.CON_CHANNEL)
            await planogramUpdatePost.send("<@&" + str(self.CON_ROLE_ID) + ">: The " + str(planogram) + " Planogram has been updated!", file=discord.File(f'planogramImg/{filename}.jpg'))

        except Exception as e:
            await ctx.send(f'An Eror Occured: {e}', ephemeral=True)


        

async def setup(bot): # Must have a setup function
    await bot.add_cog(PlanogramCommands(bot)) # Add the class to the cog.