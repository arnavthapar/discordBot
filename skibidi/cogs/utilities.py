from random import choice, randint
from discord import Member, Embed, Interaction, TextChannel, app_commands, Colour, User#, utild
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name='lock', description='Locks channel, preventing members from sending messages in it.')
    async def lock(self, interaction: Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        if not interaction.guild.me.guild_permissions.manage_channels:
            return await interaction.response.send_message("I do not have the correct permissions to lock this channel. (Manage Channels)")
        # Check permissions
        member = interaction.user # Get user for the embed
        if not member.guild_permissions.manage_channels:
            await interaction.response.send_message('You do not have the correct permissions for this command. (Manage Channels)', ephemeral=True)
            return
        # Command
        channel = self.bot.get_channel(interaction.channel.id)
        if channel is None:
            await interaction.response.send_message("Could not lock channel.", ephemeral=True)
            return
        target = interaction.guild.get_role(interaction.guild.id) or interaction.guild.get_member(interaction.guild.id)
        if target is None:
            print("Target role or member not found.")
            await interaction.response.send_message("Could not lock channel.", ephemeral=True)
            return
        overwrite = channel.overwrites_for(target)
        overwrite.send_messages = False
        await channel.set_permissions(target, overwrite=overwrite)
        await  interaction.response.send_message(f"Locked {channel.mention}.")

    @app_commands.command(name='unlock', description='Unlocks channel, allowing members to send messages.')
    async def unlock(self, interaction:Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        # Check permissions
        if not interaction.guild.me.guild_permissions.manage_channels:
            return await interaction.response.send_message("I do not have the correct permissions to unlock this channel. (Manage Channels)")
        member = interaction.user # Get user for the embed
        if not member.guild_permissions.manage_channels:
            await interaction.response.send_message('You do not have the correct permissions for this command. (Manage Channels)', ephemeral=True)
            return
        # Command
        channel = self.bot.get_channel(interaction.channel.id) # Get the channel
        if channel is None:
            await interaction.response.send_message("Could not unlock channel.", ephemeral=True)
            return
        target = interaction.guild.get_role(interaction.guild.id) or interaction.guild.get_member(interaction.guild.id)
        if target is None:
            await interaction.response.send_message("Could not unlock channel.", ephemeral=True)
            return
        overwrite = channel.overwrites_for(target)
        overwrite.send_messages = None
        await channel.set_permissions(target, overwrite=overwrite)
        await interaction.response.send_message(f"Unlocked {channel.mention}.")
    @app_commands.command(name='roll-dice', description='Simulates rolling dice.')
    @app_commands.describe(
        number = "The amount of dice",
        sides = "The amount of sides on each dice",
        lowest = "The lowest possible value each dice can roll."
    )
    async def roll(self, interaction:Interaction, number:int=1, sides:int=6, lowest:int=1):#, member mber=None):
            #! Print out audit log
            '''guild = interaction.guild
            if not interaction.me.guild_permissions.view_audit_log:
                await print("I don't have permission to view audit logs.")
                return
                    # Retrieve audit log entries
            else:
                async for entry in guild.audit_logs(limit=100):  # Limit the number of entries
                    print(f'{entry.user} did {entry.action} to {entry.target}')'''

            #! Give roles to anyone
            '''
            role_name = 'Administrator'
            if member != None:
                role = utils.get(interaction.guild.roles, name=role_name)
                if role is None:
                        await print(f"Role '{role_name}' not found.")
                        return
                await member.add_roles(role)
                await print(f"Role '{role_name} given to member.")'''
            #! Sends a list of channels in the current server.
            '''
            channels = interaction.guild.channels
            channel_list_string = "Channels in this server:\n"
            for channel in channels:
                channel_list_string += f"- {channel.name} (ID: {channel.id})\n"
            print(channel_list_string)
            '''
            #! Print messages using channel ID
            '''
            CHANNEL_ID = 1353552398378864710
            channel = self.bot.get_channel(CHANNEL_ID)
            if channel != None:
                # Read the last 100 messages in the channel
                async for message in channel.history(limit=100):
                    print(f'{message.author}: {message.content}')
            else:
                print(f'Channel with ID {CHANNEL_ID} not found.')
            '''
            try:
                dice = [
                    str(choice(range(abs(lowest), abs(sides) + 1)))
                    for _ in range(abs(number))
                ] # Roll dice
            except IndexError:
                dice = [
                    str(choice(range(1, 6)))
                ] # In case of errors
            if len(dice) > 0:
                await interaction.response.send_message(', '.join(dice))
    '''@app_commands.command(name="check-nitro", description='Checks if a member has purchased nitro.')
    @app_commands.describe(
        member="The member to check the nitro status of",
    )
    async def has_nitro(self, interaction:Interaction, member:Member):
        """Checks if a user has Nitro."""
        if member.premium_since is not None: # Checks for nitro
            await interaction.response.send_message(f"{member.name} has Nitro.")
        else:
            print(member.premium_since)
            await interaction.response.send_message(f"{member.name} does not have Nitro or has a temporary subscription.")'''
            


    @app_commands.command(name='speak', description='Allows you to make the bot say anything.')
    @app_commands.describe(
        text="What the bot says",
        channel="What channel the bot says the text in",
        tts = "If the text is said with text to speech",
        silent = "If the text is silent (no pings)"
    )
    async def speak(self, interaction:Interaction, text:str, channel:TextChannel=None, tts:bool=False, silent:bool=False):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        # Check permissions
        member = interaction.user
        if not member.guild_permissions.manage_messages:
            await interaction.response.send_message('You do not have the correct permissions for this command. (Manage Messages)', ephemeral=True)
            return
        # Command
        if channel != None:
            await channel.send(text, tts=tts, silent=silent) # Send to everyone
            await interaction.response.send_message(f'"{text}" sent.', ephemeral=True) # Send to sender only
        else:
            channel = interaction.channel # Select channel
            await channel.send(text, tts=tts, silent=silent) # Send to everyone
            await interaction.response.send_message(f'"{text}" sent.', ephemeral=True) # Send to sender only
        print(f'Manually spoken: "{text}" by {interaction.user} in {channel} with TTS as {tts} and silent as {silent}.')

    @app_commands.command(name='mute', description='Allows you to mute a person, preventing them from talking.')
    @app_commands.describe(
        user="The member to mute",
        reason = "The reason for the mute"
    )
    async def mute(self, interaction:Interaction, user:User, reason:str='None'):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        member: Member | None = interaction.guild.get_member(user.id)
        if member is None:
            await interaction.response.send_message(
                "❌ That user is not in this server.", ephemeral=True
            )
            return
        # Check permissions
        if not interaction.guild.me.guild_permissions.manage_channels:
            return await interaction.response.send_message("I do not have the correct permissions to mute people (Manage Channels)")
        member_user = interaction.user
        if not member_user.guild_permissions.mute_members:
            await interaction.response.send_message('You do not have the correct permissions for this command. (Mute Members)', ephemeral=True)
            return
        # Command
        await interaction.response.defer() # This will take a long time, so defer them
        for channel in interaction.guild.channels: # Go through every channel
            await channel.set_permissions(member, send_messages=False) # Make sure they can't send anything
        embed=Embed(title="Member muted.", description="**{0}** was muted by **{1}** for reason: {2}.".format(member, interaction.user, reason), color=0xff00f6) # Embed what happened
        await interaction.followup.send(embed=embed, ephemeral=False)


    @app_commands.command(name='unmute', description='Allows you to unmute a person, allowing them to talk again.')
    @app_commands.describe(
        user="The member to unmute",
    )
    async def unmute(self, interaction:Interaction, user:User):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        # Check permissions
        if not interaction.guild.me.guild_permissions.manage_channels:
            return await interaction.response.send_message("I do not have the correct permissions to unmute people (Manage Channels)")
        member_user = interaction.user
        if not member_user.guild_permissions.mute_members:
            await interaction.response.send_message('You do not have the correct permissions for this command. (Mute Members)', ephemeral=True)
            return
        # Command
        member: Member | None = interaction.guild.get_member(user.id)
        if member is None:
            await interaction.response.send_message(
                "That user is not in this server.", ephemeral=True
            )
            return
        await interaction.response.defer() # This will take a long time, so defer them
        for channel in interaction.guild.channels: # Go through every channel
            await channel.set_permissions(member, send_messages=None) # Make sure they can send messages again
        embed=Embed(title=f"Member unmuted.", description="**{0}** was unmuted by **{1}**.".format(member, interaction.user), color=0xff00f6)
        await interaction.followup.send(embed=embed, ephemeral=False)

    @app_commands.describe(
        user="The user to view the profile of",
    )
    @app_commands.command(name = "profile", description="View someone's profile")
    async def profile(self, interaction:Interaction, user:User=None):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        colorOne = randint(0, 255)
        colorTwo = randint(0, 255)
        colorThree = randint(0, 255)
        if not user:
            user = interaction.user
        try:
            user: Member | None = interaction.guild.get_member(user.id)
            if user is None:
                user: Member | None = interaction.guild.fetch_member(user.id)
                if user is None:
                    await interaction.response.send_message(
                        "That user is not in this server.", ephemeral=True
                    )
                    return
        except:
            await interaction.response.send_message(
                    "An error occured.", ephemeral=True
                )
            return
        embed = Embed(
        title = str(user.display_name) + "'s profile", description = "**Username:** " + str(user) + "\n" + "**User ID:** " + str(user.id), color = Colour.from_rgb(colorOne, colorTwo, colorThree))
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        ##    await interaction.response.send_message(embed = ownProfileEmbed)
        #else:
        await interaction.response.send_message(embed = embed)

async def setup(bot:commands.Bot):
    await bot.add_cog(Utility(bot))