import discord
import csv
from time import strftime
from discord.ext import commands
from discord import app_commands
import time

class LateCommands(commands.Cog, name="Late Notice Commands", description="Commands used to notify managers of being late."):

	MAX_TIME_LATE = int(15)
	MANAGER_ROLE_ID = [920698657160982578, 958433853834420265]
	MANAGER_BOT_CHANNEL = 958744862583304233
	LATE_CHANNEL = 984544002068058122
	SUCESS_EMJOI = '👍'
	ERROR_EMJOI = '❌'

	def __init__(self, bot):
		self.bot = bot

	@commands.hybrid_command(
		description="Let managers know that you will be running 15 minutes late or less!"
	)
	@app_commands.describe(minutes='The number of minutes late you expect to be. Must be between 1-15', reason='Provide a general reason for why you are running late.')
	async def late(self, ctx, minutes: int, *, reason: str):
		#await ctx.defer(ephemeral=True)
		# Check to see if channel command was used in is the propper channel
		if not (ctx.channel.id == self.LATE_CHANNEL):
			await ctx.send("You posted in the wrong channel! For the command to be valid, you must use it in the <#" + str(self.LATE_CHANNEL) + "> channel.",ephemeral=True)
			return
		else:
			pass

		reasonlate = reason.replace("’", "'").replace("‘", "'").replace("”", '"').replace("‟", '"')
		lateError = False
		try:
			timelate = int(minutes)
		except Exception as e:
			lateError = True
			#await ctx.message.add_reaction(self.ERROR_EMJOI)
			await ctx.send(ctx.message.author.mention + ": You need to specify how many minutes late you will be.",ephemeral=True)

		# Check for reason
		if reasonlate == "":
			lateError = True
			#await ctx.message.add_reaction(self.ERROR_EMJOI)
			await ctx.send(ctx.message.author.mention + ": You need to provide a reason as to why you you will be late.",ephemeral=True)
		else:
			pass

		# If no errors and under max late time, state the user is late, otherwise reply that the time is too long and to call
		if not lateError:
			if timelate <= self.MAX_TIME_LATE:
				#await ctx.message.add_reaction(self.SUCESS_EMJOI)
				mgrRoleToMention = discord.utils.get(ctx.guild.roles, id=int(self.MANAGER_ROLE_ID[0]))
				useAppCmdNote = ""
				if len(ctx.message.content) > 0 and ctx.message.content[0] == "!":
					useAppCmdNote = "\n\nIt is recommended to use the updated command for latenesses `/late` in the future. This will make it easier to make sure the current information is provided."
				await ctx.send(mgrRoleToMention.mention + ": " + ctx.message.author.display_name + " will be " + str(timelate) + " minutes late. Reason: " + reasonlate + useAppCmdNote,ephemeral=False, allowed_mentions=discord.AllowedMentions(roles=True))

				logDataRow = [ctx.message.author.display_name, str(ctx.message.author.id), strftime("%Y-%m-%d %H:%M:%S"), timelate, reasonlate]
				with open('lateLog.csv', 'a') as f:
					# create the csv writer
					writerObj = csv.writer(f)

					# write a row to the csv file
					writerObj.writerow(logDataRow)
			else:
				##Time late is too long
				#await ctx.message.add_reaction(self.ERROR_EMJOI)
				await ctx.send(ctx.message.author.mention + ": You are going to be more than " + str(self.MAX_TIME_LATE) + " minutes late. You must call the theater and speak to a manager.",ephemeral=True)
		else:
			pass


		if len(ctx.message.content) > 0 and ctx.message.content[0] == "!":
			try:
				await ctx.message.author.send("You are receiving this message because you recently used the `!late` command. You __DO NOT__ need to do the command again!!\n\nWhile there is no issue with using this command, there this bot is learning new skills and to make it easier for new users to discord, the command has changed to `/late`.\n\nUsing this new command does the same thing, but it will now prompt you for the correct values. This is easier for new users to Discord, as well as prevent errors\n\nCheck out the <#985992862980247573> channel to see the new commands and syntax.")
			except:
				pass
                

	@commands.hybrid_command(
		description="Get a sortable list of staff who have been late."
	)
	@commands.has_any_role(*MANAGER_ROLE_ID)
	async def latereport(self, ctx):
		# Check to see if channel command was used in is the propper channel
		if not (ctx.channel.id == self.MANAGER_BOT_CHANNEL): 
		    await ctx.send("You posted in the wrong channel! For the command to be valid, you must use it in the <#" + str(self.MANAGER_BOT_CHANNEL) + "> channel.")
		    return
		else:
		    # handle your else here, such as null, or log it to ur terminal
		    pass

		with open('lateLog.csv', 'rb') as fp:
			await ctx.send("Late Log Report is below: ", file=discord.File(fp, 'Late Report.txt'))



async def setup(bot): # Must have a setup function
	await bot.add_cog(LateCommands(bot)) # Add the class to the cog.