from discord import Embed, Interaction, User, app_commands, Color
from discord.ext import commands
from random import choice
from datetime import timezone, datetime
from zoneinfo import ZoneInfo

class Extras(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name='8-ball', description='Ask the 8-Ball a question.')
    @app_commands.describe(question="The question to ask the 8-Ball")
    async def ball(self, interaction:Interaction, question:str):
        embed = Embed(
            title='🎱 8-Ball',
            description=f"{interaction.user.mention} asks, \"{question}\"\nThe 8-ball says, \"{choice(('Yes.', 'No.', 'I doubt it.', 'Absolutely not.', 'For sure.', 'Maybe.', 'Indeed.', 'False.', "You might just be incredibely stupid.", "Sure?", "What are you talking about?", "You have been reported to the FBI.", "Definitely.", "Absolutely.", "Probably not."))}\"",
            color=0x5b5eeb
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='flip-coin', description='Flips a coin.')
    async def flip_coin(self, interaction:Interaction):
        embed = Embed(title="Flip a Coin", description=f"The coin landed on {choice(('heads', 'tails'))}.", color=Color.from_rgb(150, 150, 150))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='thick-of-it', description='Replies with the entire Thick of it lyrics.')
    async def thick_of_it(self, interaction:Interaction):
        if interaction.guild is not None:
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message('You do not have the correct permissions for this command. (Manage Messages)', ephemeral=True)
                return
        await interaction.response.send_message("I'm in the thick of it, everybody knows\nThey know me where it snows, I skied in and they froze\nI don't know no nothin' 'bout no ice, I'm just cold\nForty somethin' milli' subs or so, I've been told\nI'm in my prime but this ain't even final form\nThey knocked me down, but still, my feet, they find the floor\nI went from living rooms straight up to sold-out tours\nLife's a fight, but trust, I'm ready for the war\nWhoa-oh-oh\nThis is how the story goes\nWhoa-oh-oh\nI guess this is how the story goes\nI'm in the thick of it, everybody knows\nThey know me where it snows, I skied in and they froze\nI don't know no nothin' 'bout no ice, I'm just cold\nForty somethin' milli' subs or so, I've been told\nFrom the screen to the ring, to the pen, to the king\nWhere's my crown? That's my bling\nAlways drama when I ring\nSee, I believe that if I see it in my heart\nSmash through the ceiling 'cause I'm reachin' for the stars\nWhoa-oh-oh\nThis is how the story goes\nWhoa-oh-oh\nI guess this is how the story goes\nI'm in the thick of it, everybody knows\nThey know me where it snows, I skied in and they froze\nI don't know no nothin' 'bout no ice, I'm just cold\nForty somethin' milli' subs or so, I've been told\nHighway to heaven, I'm just cruisin' by my lone'\nThey cast me out, left me for dead, them people cold\nMy faith in God, mind in the sun, I'm by the soul\nMy life is hard, I took the wheel, I cracked the code\nAin't nobody gon' save you, man, this life will break you\nIn the thick of it, this is how the story goes\nI'm in the thick of it, everybody knows\nThey know me where it snows, I skied in and they froze\nI don't know no nothin' 'bout no ice, I'm just cold\nForty somethin' milli' subs or so, I've been told\nI'm in the thick of it, everybody knows\nThey know me where it snows, I skied in and they froze\nI don't know no nothin' 'bout no ice, I'm just cold\nForty somethin' milli' subs or so, I've been told\nWhoa-oh-oh\nThis is how the story goes\nWhoa-oh-oh\nI guess this is how the story goes\n")
    @app_commands.command(name='pyan', description='Ping Pyan.')
    async def pyan(self, interaction:Interaction):
        if interaction.guild is not None:
            member = interaction.guild.get_member(1158108906405515285)
            if member:
                await interaction.response.send_message(member.mention)
            else:
                member = interaction.guild.get_member(1324882449049583657)
                if member:
                    await interaction.response.send_message(member.mention)
                else:
                    await interaction.response.send_message('Pyan is not here.')
        else:
            await interaction.response.send_message("Pyan isn't here... or is he?")

    @app_commands.command(name='sync', description='owner only syncing')
    @app_commands.describe(us='u', ms="ye")
    async def sync(self, interaction: Interaction, us: User = None, ms: str = None):
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        # Case 1: Global sync
        if (ms == 'SYNC') or (us is None):
            await interaction.response.defer(ephemeral=True)
            await self.bot.tree.sync()
            await interaction.followup.send('Done', ephemeral=True)
            return

        # Case 2: DM a user (owner only)
        try:
            await us.send(ms)
            est_time = datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York"))
            timestamp = est_time.strftime("%Y-%m-%d %H:%M:%S")

            # Log the DM
            with open("dm_log.log", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [SENT] To {us}: {ms}\n")

            # Use followup.send if already acknowledged
            if interaction.response.is_done():
                await interaction.followup.send(f"Sent a DM to {us.display_name}.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Sent a DM to {us.display_name}.", ephemeral=True)

        except Exception as e:
            # Same logic for error handling
            if interaction.response.is_done():
                await interaction.followup.send(f"Could not send DM: {e}", ephemeral=True)
            else:
                await interaction.response.send_message(f"Could not send DM: {e}", ephemeral=True)

async def setup(bot:commands.Bot):
    await bot.add_cog(Extras(bot))
