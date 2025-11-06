import os
from discord import Intents, CustomActivity, ActivityType
from discord.ext import commands
from dotenv import load_dotenv


# Load up the bot
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
intentsbot = Intents.all()
intentsbot.dm_messages = True
bot = commands.Bot(
    command_prefix = commands.when_mentioned,
    description = "a fun multipurpose villager bot\n(created by fritbit)\nJoin support server at: https://discord.gg/JArnC4Y2Ug\n[🎉BACK UP AGAIN 🎉]",
    #help_command = help_command,
    intents = intentsbot
    )

bot.remove_command('help')
async def setup_hook():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            if not filename.startswith('button'):
                extension = f"cogs.{filename[:-3]}"
                await bot.load_extension(extension)
    await bot.tree.sync()
bot.setup_hook = setup_hook
@bot.event
async def on_ready():
    #await bot.change_presence(activity=Game(name="Hollow Knight"))
    await bot.change_presence(activity=CustomActivity("Minecraft", type=ActivityType.playing))
    bot.owner_id = (await bot.application_info()).owner.id
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