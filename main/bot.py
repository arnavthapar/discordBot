import os
from discord import Intents, ActivityType, CustomActivity, Message
from discord.ext import commands
from dotenv import load_dotenv
from random import randrange
from datetime import timezone, datetime
from zoneinfo import ZoneInfo

# Load up the bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
'''intentsbot = Intents.default()
intentsbot.message_content = True
intentsbot.guilds = True
intentsbot.moderation = True'''
bot = commands.Bot(
    command_prefix = commands.when_mentioned,
    description = "A very skibidi bot",
    #help_command = help_command,
    intents = Intents.all()
    )
bot.remove_command('help')
async def setup_hook():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            #if not filename.startswith('dictlist'):
                extension = f"cogs.{filename[:-3]}"
                await bot.load_extension(extension)
            #lse: await bot.modu(f"commands.{filename[:-3]}")
    await bot.tree.sync()

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    #await bot.change_presence(activity=Game(name="Hollow Knight"))
    await bot.change_presence(activity=CustomActivity("wait", type=ActivityType.custom))
    for i in bot.guilds:
        if i.id not in (1324878748339929118, 1353550177230782545):
            print(i)
    bot.owner_id = (await bot.application_info()).owner.id
@bot.event
async def on_message(message:Message):
    if message.author == bot.user:
        return

    if message.content == ('skibidi toilet') and randrange(1, 4) == 1:
        await message.add_reaction('👎')  # React with thumbs down
    if ('pyan' in message.content) and (message.guild.id == 1324878748339929118) and randrange (1, 4) == 1:
        await message.add_reaction(bot.get_emoji(1349534044500525237))
                # Ignore messages from the bot itself

    # Convert UTC to EST (handles Daylight Saving automatically)
    est_time = message.created_at.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("America/New_York"))
    timestamp = est_time.strftime("%Y-%m-%d %H:%M:%S")

    # Case 1: Direct message to the bot (no guild)
    if message.guild is None:
        log_line = f"[{timestamp}] [DM] {message.author}: {message.content}"
        print(log_line)
        try:
            with open("dm_log.log", "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception as e:
            print(f"Failed to write log: {e}")
        return

    # Case 2: Message that mentions (pings) the bot
    elif bot.user.mentioned_in(message) and not message.mention_everyone:
        log_line = f"[{timestamp}] [{message.guild.name}] {message.author}: {message.content}"
        print(log_line)
        try:
            with open("dm_log.log", "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception as e:
            print(f"Failed to write log: {e}")
        return

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You did not send all the necessary parameters.')
    elif isinstance(error, commands.CommandNotFound):
        #await ctx.send("Command not found. Remember to use / and not !.")
        pass

bot.run(TOKEN)