from discord import Member, Interaction, app_commands, Embed, ui, ButtonStyle, Color
from discord.ext import commands
from mysql.connector import connect
from random import choice, randrange


class Gamble(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="speak", description="Make the bot say anything.")
    @app_commands.describe(
        message="The message the bot will say.",
    )
    async def speak(self, interaction: Interaction, message:str):
        channel = interaction.channel # Select channel
        await channel.send(message) # Send to everyone
        await interaction.response.send_message(f'"{message}" sent.', ephemeral=True) # Send to sender only

async def setup(bot: commands.Bot):
    await bot.add_cog(Gamble(bot))
