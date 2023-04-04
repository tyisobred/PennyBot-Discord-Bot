import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
from asyncio import TimeoutError, sleep
from datetime import datetime

class VerificationCommands(commands.Cog, name="Verification Commands", description="Commands used to indentify and confirm staff."):
    
    MANAGER_ROLE_ID = [920698657160982578, 958433853834420265,1044058355330723850]
    VERIFICATION_CHNL = 994702874305118249
    RULES_CHNL = 933193366034866196


    VERIFY_POST = "Click the red button below to verify your indentify!"
    RULES_POST = "Welcome to the Egyptian 24 Staff Discord!\n\nBefore you can access the full server, you must read and acknowledge the rules below. This server is monitored by your managers and any discussions on this server should be work appropriate!\n\n> 1. You must set your nickname to your real name on this server so everyone knows who you are. \n\n> 2. Be respectful to others. If you wouldn't say or do it at work, do not say or do it here. All guidelines from the employee handbook apply to the discord server\n\n> 3. The purpose of this server is to allow staff a way to communicate with your co-workers outside of work as well as share important information.\n\n> 4. This server is NOT to be used to call out! You are required to call the theater and speak to a manager if you need to call out. We do however allow the server to be used to let us know if you are running slightly late. Please use the correct channel and the command so we are notified. You can only use Discord if running less than 15 minutes late.\n\n> 5. Please try to use the proper channel to keep things clean organized and easy to read.\n\n**If you agree to follow these rules, and all other policies from the employee handbook, press the button below!** \nOnce you agree to follow these rules, you can go back and see the rest of the channels. These rules may be updated as needed, and occasionally all staff will need to re-acknowledge the rules. If you are not following the rules, you may end up with limited access to the server."

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="MANAGERS ONLY",
        brief="MANAGERS ONLY"
    )
    @commands.has_any_role(*MANAGER_ROLE_ID)
    async def setupVerify(self, ctx):
        verificationChannel = self.bot.get_channel(self.VERIFICATION_CHNL)
        await verificationChannel.send(self.VERIFY_POST, view=PersistentView())

    @commands.command(
        help="MANAGERS ONLY",
        brief="MANAGERS ONLY"
    )
    @commands.has_any_role(*MANAGER_ROLE_ID)
    async def setupRules(self, ctx):
        rulesChannel = self.bot.get_channel(self.RULES_CHNL)
        await rulesChannel.send(self.RULES_POST, view=PersistentViewRules())

    @commands.hybrid_command(
        description="Sets Employee Date of Hire"
    )
    @app_commands.describe(employee='Employee to set Date of Hire for', dateofhire="Employee's date of hire in format MM/DD/YYYY")
    @commands.has_any_role(*MANAGER_ROLE_ID)
    async def setdateofhire(self, ctx, employee: discord.Member, dateofhire):
        
        empDoH = datetime.strptime(dateofhire, '%m/%d/%Y').date()
        with open('empHireDates.txt', 'a') as empHireDateFile:
            empHireDateFile.write(str(empDoH) + "," + str(employee.id))

        await ctx.reply("Employee: " + str(employee.display_name) + " date of hire has been set to " + str(empDoH), ephemeral=True)


async def setup(bot): # Must have a setup function
    await bot.add_cog(VerificationCommands(bot)) # Add the class to the cog.


class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Verify', style=discord.ButtonStyle.red, custom_id='PennyBot:Verify_Staff')
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerificationModal())



class PersistentViewRules(discord.ui.View):
    AGE_POST = "Choose if you are a minor or adult. This is also so that these groups can be notified seperately."    
    POS_POST = "Choose your normally scheduled positions from the list below. This will be used to help direct department-specific topics to those team members.\n\n**NOTE: **Once you pick up a role, you are not able to change it yourself"

    ACCEPTED_RULES_ROLE_ID = 933128370701598750

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='I Agree to the Rules', style=discord.ButtonStyle.red, emoji="😺", custom_id='PennyBot:Accept_Rules')
    async def verifyRules(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(self.ACCEPTED_RULES_ROLE_ID) in str(interaction.user.roles):
            await interaction.response.send_message('You have already accepted the rules!', ephemeral=True)
        else:
            role = discord.utils.get(interaction.guild.roles, id=self.ACCEPTED_RULES_ROLE_ID)
            await interaction.user.add_roles(role)

            await interaction.response.send_message(interaction.user.mention + ": Thanks for accepting! Please also make sure to set your positions and age!", ephemeral=True)

    @discord.ui.button(label='Select Positions', style=discord.ButtonStyle.blurple, custom_id='PennyBot:PosiBtn')
    async def dispRolePosDrop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(self.POS_POST, view=PersistentViewPosistion(), ephemeral=True)

    @discord.ui.button(label='Minor or Adult??', style=discord.ButtonStyle.grey, custom_id='PennyBot:AgeBtn')
    async def dispRoleAgeDrop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(self.AGE_POST, view=PersistentViewAge(), ephemeral=True)


class PersistentViewPosistion(discord.ui.View):
    CON_ROLE_ID = 933198816218337301
    USH_ROLE_ID = 933199063216693268
    BOX_ROLE_ID = 933199181865181204
    CAFE_ROLE_ID = 934651728429715456
    HS_ROLE_ID = 933600556017127444

    LIST_ROLES=[CON_ROLE_ID,USH_ROLE_ID,BOX_ROLE_ID,CAFE_ROLE_ID,HS_ROLE_ID]

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.select(
        custom_id='PennyBot:Select_Pos', # the decorator that lets you specify the properties of the select menu
        placeholder = "Pick you normally scheduled position", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 5, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label='Concession', 
                value=CON_ROLE_ID,
                description='Role for concession Team Members',
                emoji="🍿"
            ),
            discord.SelectOption(
                label='Usher', 
                value=USH_ROLE_ID,
                description='Role for Ushers Team Members',
                emoji="🧹"
            ),
            discord.SelectOption(
                label='Box Office', 
                value=BOX_ROLE_ID,
                description='Role for Box or Guest Services Team Members',
                emoji="🎟"
            ),
            discord.SelectOption(
                label='Cafe', 
                value=CAFE_ROLE_ID,
                description='Role for Cafe Team Members',
                emoji="🧋"
            ),
            discord.SelectOption(
                label='Pizza Hut / Hot Spot', 
                value=HS_ROLE_ID,
                description='Role for Hot Spot or Pizza Hut Team Members',
                emoji="🍕"
            )
        ])
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        selectedRoles = []
        memRoles = interaction.user.roles

        for roleID in select.values:
            roleItem = discord.utils.get(interaction.guild.roles, id=int(roleID))
            if not roleID in memRoles:
                if roleItem != None:
                    selectedRoles.append(roleItem)

        rolesToRemove = []
        rolesToAdd = []
        for roleID in self.LIST_ROLES:
            if str(roleID) in select.values:
                if str(roleID) in str(memRoles):
                    pass
                    #    print(f"Role {roleID} is already present and is selected. Do nothing")
                else:
                    rolesToAdd.append(discord.utils.get(interaction.guild.roles, id=int(roleID)))
            else:
                if str(roleID) in str(memRoles):
                    rolesToRemove.append(discord.utils.get(interaction.guild.roles, id=int(roleID)))
                #else:
                #    print(f"Role {roleID} is NOT present and is not selected. DO NOTHING")
            
        if len(rolesToRemove) > 0:
            await interaction.user.remove_roles(*rolesToRemove)
        if len(rolesToAdd) > 0:
            await interaction.user.add_roles(*rolesToAdd)


        await interaction.response.send_message("Your position roles have been updated.", ephemeral=True)




class PersistentViewAge(discord.ui.View):
    ADU_ROLE_ID = 985999975819403274
    MIN_ROLE_ID = 985952616427180132

    LIST_ROLES=[ADU_ROLE_ID,MIN_ROLE_ID]

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.select(
        custom_id='PennyBot:Select_Age', # the decorator that lets you specify the properties of the select menu
        placeholder = "Select if you are a minor or adult", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label='Minor', 
                value=MIN_ROLE_ID,
                description='For Team Members that are minors (<18yrs old)',
                emoji="🔞"
            ),
            discord.SelectOption(
                label='Adult', 
                value=ADU_ROLE_ID,
                description='For Team Members that are minors (<18yrs old)',
                emoji="💾"
            )
        ])
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        selectedRoles = []
        memRoles = interaction.user.roles

        for roleID in select.values:
            roleItem = discord.utils.get(interaction.guild.roles, id=int(roleID))
            if not roleID in memRoles:
                if roleItem != None:
                    selectedRoles.append(roleItem)

        rolesToRemove = []
        rolesToAdd = []
        for roleID in self.LIST_ROLES:
            if str(roleID) in select.values:
                if str(roleID) in str(memRoles):
                    pass
                    #    print(f"Role {roleID} is already present and is selected. Do nothing")
                else:
                    rolesToAdd.append(discord.utils.get(interaction.guild.roles, id=int(roleID)))
            else:
                if str(roleID) in str(memRoles):
                    rolesToRemove.append(discord.utils.get(interaction.guild.roles, id=int(roleID)))
                #else:
                #    print(f"Role {roleID} is NOT present and is not selected. DO NOTHING")
            
        if len(rolesToRemove) > 0:
            await interaction.user.remove_roles(*rolesToRemove)
        if len(rolesToAdd) > 0:
            await interaction.user.add_roles(*rolesToAdd)


        await interaction.response.send_message("Your age role has been updated.", ephemeral=True)




class VerificationModal(discord.ui.Modal, title='Verification of Staff'):
    name = discord.ui.TextInput(
        label='What is your name?',
        placeholder='First Name & Last Initial. . .',
        required=True
    )

    verificationQ = discord.ui.TextInput(
        label='What is the name of the General Manager?',
        placeholder='Use format: "Mr/Mrs. NAME". . .',
        required=True
    )

    dateOfdHireQ = discord.ui.TextInput(
        label='What is your Date of Hire? (MM/DD/YYYY)',
        placeholder='MM/DD/YYYY',
        min_length=10,
        max_length=10,
        required=True
    )

    GENERAL_MGR_NAME = ['mr. v']
    VERIFIED_ROLE_ID = 994703994305904811
    RULES_CHANNEL_ID = 933193366034866196
    DEFAULT_LOGS = 933204353408438272

    async def on_submit(self, interaction: discord.Interaction):
        if str(self.VERIFIED_ROLE_ID) in str(interaction.user.roles):
            await interaction.response.send_message('You have already accepted the rules!', ephemeral=True)
            return
        defaultLogChn = interaction.client.get_channel(self.DEFAULT_LOGS)
        
        nickname = str(self.name.value)
        if self.verificationQ.value.lower() in self.GENERAL_MGR_NAME:
            await interaction.user.edit(nick=nickname)

            role = discord.utils.get(interaction.guild.roles, id=self.VERIFIED_ROLE_ID)
            await interaction.user.add_roles(role)

            empDoH = datetime.strptime(self.dateOfdHireQ.value, '%m/%d/%Y').date()
            with open('empHireDates.txt', 'a') as empHireDateFile:
                empHireDateFile.write(str(empDoH) + "," + str(interaction.user.id))

            await interaction.response.send_message(interaction.user.mention + ": Your account has been verified. Please go to the <#" + str(self.RULES_CHANNEL_ID) + "> channel and follow all the instructions in that channel to gain access to the rest of the server.\n\nIt is also recommended to check the Commands channel after you accept the rules to see how to use some of the commands we have.", ephemeral=True)

            verfEmbed = discord.Embed(title="New User Verified", description="The user listed below has been verified.", color=0x009414)
            verfEmbed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            verfEmbed.add_field(name="Name:", value=nickname, inline=True)
            verfEmbed.add_field(name="Verification Question Answer:", value=self.verificationQ.value, inline=True)
            verfEmbed.add_field(name="Date of Hire Answer:", value=empDoH, inline=True)

            await defaultLogChn.send("The following user has been verified", embed=verfEmbed)
        else:
            await interaction.response.send_message('The verification question was incorrect. Please try again or see a manager.', ephemeral=True)

            verfEmbed = discord.Embed(title="Error: Verification", description="The user listed below could __NOT__ be verified", color=0x99110c)
            verfEmbed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            verfEmbed.add_field(name="Name:", value=nickname, inline=True)
            verfEmbed.add_field(name="Verification Question Answer:", value='"' + str(self.verificationQ.value) + '"', inline=True)
            verfEmbed.add_field(name="Date of Hire Answer:", value=self.verificationQ.value, inline=True)

            await defaultLogChn.send("The following user has **__NOT__** been verified", embed=verfEmbed)



