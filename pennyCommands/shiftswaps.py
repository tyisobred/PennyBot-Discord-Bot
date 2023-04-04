import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal,get_args
import datetime
import json

class ShiftOfferCommands(commands.Cog, name="Shift Offer Commands", description="Advertise a shift that may be available for grabs!"):

    SHIFT_CHANNEL = 920695190287700038
    MANAGER_ROLE_ID = [920698657160982578, 958433853834420265]
    POSITION_LITERAL = Literal['Con', 'Usher', 'Box', 'HS', 'PH', 'Cafe', 'SIAT']
    
    POSITION_LIST = list(get_args(POSITION_LITERAL))

    def __init__(self, bot):
        self.bot = bot

    def validateDate(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%m/%d/%y')
            return True
        except ValueError:
            return False

    @commands.hybrid_command(
        description="Add your shift to the advertised list of shifts available."
    )
    @app_commands.describe(
        shiftdate='The date of the shift you are trying to have covered in format MM/DD/YY', 
        shiftstart='Start time of your shift in the format "5:00 PM"',
        shiftend='End time of your shift in the format "1:00 AM"',
        position='Chose the position you are scheduled to work'
    )
    async def offershift(self, ctx, shiftdate: str, shiftstart: str, shiftend: str, position: POSITION_LITERAL):
        await ctx.defer(ephemeral=True)

        # Check to see if channel command was used in is the propper channel
        if not (ctx.channel.id == self.SHIFT_CHANNEL):
            await ctx.send("You posted in the wrong channel! For the command to be valid, you must use it in the <#" + str(self.SHIFT_CHANNEL) + "> channel.",ephemeral=True)
            return
        elif len(shiftstart) > 8 or len(shiftend) > 8 or ('open' in shiftstart.lower() or 'clos' in shiftend.lower()):
            await ctx.send("Your shift start or end time seems to be incorrect format. Please use the format \"H:MM [AM/PM]\". \n\nFor example, \"5:30 PM\" is acceptable, \"5:30:00 PM\" is not.",ephemeral=True)
            return
        elif not self.validateDate(shiftdate):
            await ctx.send("Your date does not seem to be in the correct format. Please use the format \"MM/DD/YY\". \n\nFor example, \"07/10/22\" is acceptable, \"Tuesday June 10\" is not.",ephemeral=True)
            return
        else:
            pass


        with open("shiftOffers.txt", 'r') as f:
            shiftData = json.load(f)

        with open("shiftOffers.txt", 'w') as f:
            entry = {"date": shiftdate, "start": shiftstart, "end": shiftend, "pos": str(position), "usr": ctx.author.id}
            shiftData.append(entry)
            shiftData = sorted(shiftData, key=lambda d: datetime.datetime.strptime(d['date'], '%m/%d/%y')) 
            json.dump(shiftData, f)



        shiftEmbed = discord.Embed(title="A shift is up for grabs!", description="The team meber below is offering their shift. \nIf you wish to take the shift, confirm with the team member that it is still open and then both of you email to let a manager know.", color=0xb1ff2b)
        shiftEmbed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
        shiftEmbed.add_field(name="Date of Shift", value=shiftdate, inline=False)
        shiftEmbed.add_field(name="Start Time", value=shiftstart, inline=True)
        shiftEmbed.add_field(name="End Time", value=shiftend, inline=True)
        shiftEmbed.add_field(name="Shift Position", value=str(position), inline=True)
        await ctx.send("Please note that if no one is able to take your shift, you are still responsible to get your shift covered or show up for work. Putting your shift in the Discord server does not constitute calling out, and if you are still unable to come in for work without findind coverage, you need to call the theater to speak to a manager. ", ephemeral=True)
        
        shifXcChn = self.bot.get_channel(self.SHIFT_CHANNEL)
        await shifXcChn.send(embed=shiftEmbed)



    @commands.hybrid_command(
        description="Display the list of all shift offers in the list currently."
    )
    @app_commands.describe(
        private='MANAGER ONLY OPTION: Set to False you want all staff to see the results.'
    )
    async def displayshifts(self, ctx, private: bool=True):
        # Check to see if channel command was used in is the propper channel
        if not (ctx.channel.id == self.SHIFT_CHANNEL):
            await ctx.send("You posted in the wrong channel! For the command to be valid, you must use it in the <#" + str(self.SHIFT_CHANNEL) + "> channel.",ephemeral=True)
            return

        if not private:
            roleCheck = False
            for mgrRoles in self.MANAGER_ROLE_ID:
                role = discord.utils.get(ctx.guild.roles, id=mgrRoles)
                if role in ctx.author.roles:
                    print("User has MGR Role")
                    roleCheck = True
                    break

            if roleCheck:
                private = False

        await ctx.defer(ephemeral=private)

        updatedShiftData = []
        msg="The following shifts may be open for grabs. Please reach out to the team member that is listed to see if their shift is still open!\n\n"

        with open("shiftOffers.txt", 'r') as f:
            shiftData = json.load(f)

        for shift in shiftData:
            if datetime.datetime.strptime(shift['date'], '%m/%d/%y').date() >= datetime.datetime.today().date():
                updatedShiftData.append(shift)
                msg=msg + "**Date: **" + str(shift['date']) + " in " + str(shift['pos']) + " for <@" + str(shift['usr']) + ">\n**Start:** " + str(shift['start']) + " --> **End:** " + str(shift['end']) + "\n\n\n"

        with open("shiftOffers.txt", 'w') as f:
            json.dump(updatedShiftData, f)

        await ctx.send(msg, ephemeral=private)





async def setup(bot): # Must have a setup function
    await bot.add_cog(ShiftOfferCommands(bot)) # Add the class to the cog.