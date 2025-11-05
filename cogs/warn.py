from discord import Member, Interaction, app_commands, User
from discord.ext import commands
from mysql.connector import connect, Error
from datetime import timedelta
class Warn(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name='warn', description='Warn user.')
    @app_commands.describe(
        member="The member to warn",
        reason="The reason the member is warned"
    )
    async def warn(self, interaction: Interaction, member:User, reason:str="None"):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        # Check permissions
        if not ((interaction.user.guild_permissions.mute_members or interaction.user.guild_permissions.administrator) or (interaction.user.id == self.bot.owner_id)):
            await interaction.response.send_message('You do not have the correct permissions for this command. (Mute Members)', ephemeral=True)
            return
        # Command
        if member.id == interaction.guild.owner_id:
            await interaction.response.send_message('You cannot warn the owner of the server.', ephemeral=True)
            return
        #user = interaction.guild.get_member(member.id)
        #user: Member | None = interaction.guild.get_member(user.id)
        cnx = connect(user='root', database='discord')
        cursor = cnx.cursor(buffered=True)
        cursor.execute(f'SELECT * FROM warns WHERE user="{member}" AND server="{interaction.guild}";')
        warns = cursor.fetchall()
        if warns == []:
            cursor.execute(f'INSERT INTO warns(user, server, amount) VALUES("{member}", "{interaction.guild}", "1")')
            warns_change = 1
        else:
            warns_change = int(warns[0][2]) + 1
            cursor.execute(f'UPDATE warns SET amount="{warns_change}"')
        cnx.commit()
        cnx.close()
        cursor.close()
        if warns_change > 1:
            s = "s"
        else: s= ""
        if warns_change > 1 and warns_change < 5:
            await interaction.response.defer()
            if warns_change == 2:
                time_delta = timedelta(seconds=86400)
            if warns_change == 3:
                time_delta = timedelta(seconds=259200)
            if warns_change == 4:
                time_delta = timedelta(seconds=604800)
            try:
                await member.timeout(time_delta, reason=f"Recieved {warns_change} total warns for reason: {reason}.")
            except:
                pass
            await interaction.followup.send(f'🚨{member.mention} was warned! They now have {warns_change} warn{s}. Reason: {reason}.🚨')
            return
        if warns_change == 5:
            try:
                await member.ban(reason=f"Received 5 warns for reason: {reason}.")
            except: pass
        await interaction.response.send_message(f'🚨{member.mention} was warned! They now have {warns_change} warn{s}. Reason: {reason}.🚨')

    @app_commands.command(name='reset_warns', description='Reset user\'s warn count.')
    @app_commands.describe(
        member="The member to remove the warns from",
    )
    async def reset_warns(self, interaction: Interaction, member:User):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        # Check permissions
        if not (interaction.user.guild_permissions.mute_members or interaction.user.guild_permissions.administrator or (interaction.user.id == self.bot.owner_id)):
            await interaction.response.send_message('You do not have the correct permissions for this command. (Mute Members)', ephemeral=True)
            return
        if interaction.user.id == 1158108906405515285:
            await interaction.response.send_message('nuh uh, not for you pyan', ephemeral=True)
            return
        # Command
        cnx = connect(user='root', database='discord')
        cursor = cnx.cursor(buffered=True)
        cursor.execute(f'SELECT * FROM warns WHERE user="{member}" AND server="{interaction.guild}";')
        warns = cursor.fetchall()
        if warns == []:
            await interaction.response.send_message(f'{member.mention} does not have any warns to clear.')
            return
        try:
            cursor.execute(f'DELETE FROM warns WHERE user="{member}" AND server="{interaction.guild}"')
            cnx.commit()
        except Exception as err:
            await interaction.response.send_message("There was an error removing warns. Please try again later.", ephemeral=True)
            print(err)
            return
        cnx.close()
        cursor.close()
        await interaction.response.send_message(f'{member.mention} was cleared of their warns.')
    @app_commands.command(name='remove-warns', description='Remove a set number of warns from a user.')
    @app_commands.describe(
        member="The member to remove the warns from",
        number="The number of warns removed"
    )
    async def removewarns(self, interaction: Interaction, member:User, number:int):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        # Check permissions
        if not (interaction.user.guild_permissions.mute_members or interaction.user.guild_permissions.administrator or (interaction.user.id == self.bot.owner_id)):
            await interaction.response.send_message('You do not have the correct permissions for this command. (Mute Members)', ephemeral=True)
            return
        if member == None:
            member = interaction.user
        if interaction.user.id == 1158108906405515285:
            await interaction.response.send_message('nuh uh, not for you pyan', ephemeral=True)
            return
        # Command
        if number < 1:
            await interaction.response.send_message('You cannot remove less than one warn.', ephemeral=True)
            return
        cnx = connect(user='root', database='discord')
        cursor = cnx.cursor(buffered=True)
        cursor.execute(f'SELECT * FROM warns WHERE user="{member}" AND server="{interaction.guild}";')
        warns = cursor.fetchall()
        if warns == []:
            await interaction.response.send_message(f'{member.mention} does not have any warns to remove.')
            return
        try:
        #if 1 == 1:
            x = int(warns[0][2]) - number
            if x <= 0:
                number -= abs(x)
                cursor.execute(f'DELETE FROM warns WHERE user="{member}" AND server="{interaction.guild}"')
            else:
                cursor.execute(f'UPDATE warns SET amount="{x}"')
            cnx.commit()
        except Error as err:
            await interaction.response.send_message("There was a SQL error removing warns. Please try again later.", ephemeral=True)
            print(err)
            return
        except Exception as err:
            await interaction.response.send_message("There was an error removing warns. Please try again later.", ephemeral=True)
            print(err)
            return
        cnx.close()
        cursor.close()
        s = "" if number == 1 else "s"
        await interaction.response.send_message(f'{member.mention} was pardoned of {number} warns{s}.')
    @app_commands.command(name='check-warns', description='Check user\'s warn count.')
    @app_commands.describe(
        member="The member to check the warns of",
    )
    async def checkwarns(self, interaction: Interaction, member:User=None):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        # Command
        member = interaction.guild.get_member(member.id)
        if member == None:
            member = interaction.user
        cnx = connect(user='root', database='discord')
        cursor = cnx.cursor(buffered=True)
        cursor.execute(f'SELECT * FROM warns WHERE user="{member}" AND server="{interaction.guild}";')
        warns = cursor.fetchall()
        cnx.close()
        cursor.close()
        if warns != []:
            await interaction.response.send_message(f'{member.mention} has {warns[0][2]} warn(s).')
            return
        await interaction.response.send_message(f'{member.mention} has no warns.')

async def setup(bot):
    await bot.add_cog(Warn(bot))