import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
from asyncio import sleep
from typing import Literal
import os.path
import logging
import csv
import json
import random

class TriviaGame(commands.Cog, name="Movie Trivia Game", description="Play some movie trivia!"):
    
    MANAGER_ROLE_ID = [920698657160982578, 958433853834420265, 1044058355330723850]

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        description="Display Trivia Game Stats"
    )
    async def triviascores(self, ctx, scoretype: Literal['All Time', 'Current Game']):

        if scoretype == "All Time":
            with open('triviaGame/alltime.csv', 'rb') as fp:
                await ctx.send("Top 10 All-Time winners are below: ", file=discord.File(fp, 'Top 10 All-Time Scores.txt'), ephemeral=True)
            return

        elif scoretype =="Current Game":
            try:
                with open('triviaGame/curGame.csv', 'rb') as fp:
                    await ctx.send("Top 10 current game users are below: ", file=discord.File(fp, 'Top 10 Current Game.txt'), ephemeral=True)
                return
            except:
                await ctx.send("There does not seem to be a game active at this time. If there is a game going, please let the host know.", ephemeral=True)
                return

        else:
            await ctx.send("The score type you entered seem incorrect. Please check the command and try again.", ephemeral=True)
            return






    @commands.hybrid_command(
        description="Start a round of Trivia"
    )
    @app_commands.describe(
        gamelength = 'How many hours will the round last? (1-24)',
        questionlimit = 'How many seconds do contestants have to answer each question? Between 30 and 120 seconds',
        numquestions = 'Number of questions in the round (5-25)'
    )
    async def triviastart(self, ctx, gamelength: int, questionlimit: int, numquestions: int):
        if os.path.isfile('triviaGame/curGame.csv'):
            await ctx.send("There is already a trivia game running. Please wait to start a new game until this one ends.", ephemeral=True)
            return

        if gamelength < 1 or gamelength > 24:
            await ctx.send("The length of the round must be between 1 & 24 hours.", ephemeral=True)
            return

        if questionlimit < 30 or questionlimit > 120:
            await ctx.send("The time to answer each question must be between 30 seconds and 120 seconds.", ephemeral=True)
            return

        if numquestions < 5 or numquestions > 25:
            await ctx.send("The number of questions per round must be between 5 and 25 questions.", ephemeral=True)
            return


        with open('triviaGame/curGame.csv', 'x') as fp:
            logging.info("Trivia Game: New game created!")

        # Create Round question set from master question list
        questionSet = []
        with open('triviaGame/gameQuestions.csv', 'w') as roundFile:
            logging.info("Trivia Game: Question set file created!")

            with open('triviaGame/masterQuestionList.csv', 'r', encoding='utf-8-sig') as masterFile:
                reader = csv.DictReader(masterFile)
                for row in reader:
                    questionSet.append(row)

            json.dump(random.sample(questionSet, numquestions), roundFile)









        trivEmbed = discord.Embed(title="Trivia Game Started", description="Your movie trivia game is starting. ", color=0x009414)
        trivEmbed.add_field(name="Game ID:", value="0000000000", inline=True)
        trivEmbed.add_field(name="Length of Game (hr):", value=gamelength, inline=True)
        trivEmbed.add_field(name="Time per question (sec):", value=questionlimit, inline=True)
        trivEmbed.add_field(name="Number of Questions:", value=numquestions, inline=True)

        await ctx.send(embed=trivEmbed, ephemeral=True)



        triviaView = TriviaGameStartView(gamelength, questionlimit, numquestions)
        annonMsg = await ctx.channel.send(ctx.author.mention + " has started a game of Movie Trivia! Click the button below to play!", view=triviaView)

        print("Trivia Game Round Active!")
        roundTimeLimit = gamelength*60*60


        await sleep(roundTimeLimit / 3) #Game is 1/3 done
        await annonMsg.edit(content=ctx.author.mention + " has started a game of Movie Trivia! Click the button below to play!\n\nThis round ends in " + str((roundTimeLimit - (roundTimeLimit / 3)) / 60) + " minutes!")
        await sleep(roundTimeLimit / 3) #Game is 2/3 done
        await annonMsg.edit(content=ctx.author.mention + " has started a game of Movie Trivia! Click the button below to play!\n\nThis round ends in " + str((roundTimeLimit - (roundTimeLimit / 3) - (roundTimeLimit / 3)) / 60) + " minutes!")
        await sleep(roundTimeLimit / 3) #Game is done
        await annonMsg.edit(content="This Trivia Game has ended. Winners will be announced shortly!", view=None)


        #calculate winners. Update annonMsg. Reply to annonMsg with winners to put at present in discord.


        print("Trivia Game Round has Ended!")
        try:
            os.remove('triviaGame/curGame.csv')
        except Exception as e:
            logging.error("Trivia Game: Error deleting curGame.csv file at end of game.")













class TriviaGameStartView(discord.ui.View):
    def __init__(self, gameLength, questionLimit, questionMax):
        super().__init__(timeout=gameLength*60*60)
        self.questionLimit = questionLimit
        self.questionMax = questionMax

    @discord.ui.button(label='Play Game', style=discord.ButtonStyle.blurple, custom_id='PennyBot:Play_Trivia')
    async def startTriviaGame(self, interaction: discord.Interaction, button: discord.ui.Button):
        triviaQuestionView = TriviaGameQuestionView(self.questionLimit, 1, self.questionMax)
        await interaction.response.send_message("Press the button below for the first question! Answer quick, as you only have a short time to answer!", view=triviaQuestionView, ephemeral=True)

        

class TriviaGameQuestionView(discord.ui.View):
    def __init__(self, questionLimit, questionNum, maxQuestions):
        super().__init__(timeout=questionLimit)
        self.questionLimit = questionLimit
        self.questionNum = questionNum
        self.questionMax = maxQuestions
        self.curAnswer = None
        self.disabled = False


    @discord.ui.select(
        custom_id='PennyBot:Tivia_Question', 
        placeholder = "Choose the correct answer",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label='Concession', 
                value='Concession'
            ),
            discord.SelectOption(
                label='Usher', 
                value='Usher'
            ),
            discord.SelectOption(
                label='Box Office', 
                value='Box Office'
            ),
            discord.SelectOption(
                label='Cafe', 
                value='Cafe'
            )
        ])

    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if not self.disabled:
            self.disabled = True
            self.curAnswer = str(select.values[0])

            if self.questionNum + 1 <= self.questionMax:
                await interaction.response.send_message("You answered: " + self.curAnswer + ". The next question will appear in 5 seconds.", ephemeral=True)

                await sleep(5)
                await interaction.delete_original_response()

                triviaQuestionView = TriviaGameQuestionView(self.questionLimit, self.questionNum + 1, self.questionMax)
                await interaction.followup.send("You are now moving to Question #" + str((self.questionNum + 1)), view=triviaQuestionView, ephemeral=True)
            else:
                await interaction.response.send_message("You have answered all the questions. Your answers have been submitted and results will be posted soon!", ephemeral=True)
        else:
                await interaction.response.send_message("You already answered this question and cannot change your answer. The answer recorded was: " + self.curAnswer, ephemeral=True)



## need to add timeout handler. currently silently fails if timeed out. 





async def setup(bot): # Must have a setup function
    await bot.add_cog(TriviaGame(bot)) # Add the class to the cog.






































