import os
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv


# Load up the bot
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
intentsbot = Intents.default()
intentsbot.dm_messages = True
bot = commands.Bot(
    command_prefix = commands.when_mentioned,
    description = "there's more where this came from",
    #help_command = help_command,
    intents = intentsbot
    )

bot.remove_command('help')
async def setup_hook():
    for filename in os.listdir():
        if filename.endswith("command.py"):
            await bot.load_extension(filename[:-3])
    await bot.tree.sync()
bot.setup_hook = setup_hook

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You did not send all the necessary parameters.')
    elif isinstance(error, commands.CommandNotFound):
        pass
        #await ctx.send("Command not found. Remember to use / and not !.")
bot.run(TOKEN)