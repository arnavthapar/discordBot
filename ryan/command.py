from discord import  Interaction, app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name='nothing', description='nothing.')
    async def nothing(self, interaction:Interaction, nothing:str, nothing2:bool=False, nothing3:bool=False):
            # Check permissions
            id = interaction.user.id
            if id != 1054537051527188482:
                return await interaction.response.send_message('this command does not exist, what are you doing?', ephemeral=True)
            # Command
            channel = interaction.channel # Select channel
            await channel.send(nothing, tts=nothing2, silent=nothing3) # Send to everyone
            await interaction.response.send_message(f'"{nothing}" sent.', ephemeral=True) # Send to sender only

async def setup(bot:commands.Bot):
    await bot.add_cog(Utility(bot))