from discord import Member, Interaction, app_commands, Embed, ui, ButtonStyle, Color
from discord.ext import commands
from mysql.connector import connect
from random import choice, randrange


class SimpleView(ui.View):
    def __init__(self, bot:commands.Bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id

    @ui.button(label="Gift Leaderboard", style=ButtonStyle.blurple)
    async def gifted(self, interaction: Interaction, _: ui.Button):
        # Fetch top 10 by gifted column
        cnx = connect(user="root", database="discord")
        cursor = cnx.cursor(buffered=True)
        cursor.execute(f'SELECT * FROM coins WHERE server="{self.guild_id}" ORDER BY gifted DESC, coins DESC LIMIT 10;')
        top_gifters = cursor.fetchall()

        description = ""
        for index, row in enumerate(top_gifters, start=1):
            user = await self.bot.fetch_user(int(row[0]))
            if index == 1:
                description += f"**{index}.** 🥇 {user.display_name} - `{row[3]} coin{"s" if int(row[3]) != 1 else ""} gifted`\n"
                imageUrl = user.display_avatar.url
            elif index == 2:
                description += f"**{index}.** 🥈 {user.display_name} - `{row[3]} coin{"s" if int(row[3]) != 1 else ""} gifted`\n"
            elif index == 3:
                description += f"**{index}.** 🥉 {user.display_name} - `{row[3]} coin{"s" if int(row[3]) != 1 else ""} gifted`\n"
            else:
                description += f"**{index}.** {user.display_name} - `{row[3]} coin{"s" if int(row[3]) != 1 else ""} gifted`\n"

        embed = Embed(title="🎁 Top 10 Gifters", description=description, color = Color.from_rgb(225, 25, 0))
        embed.set_thumbnail(url=imageUrl)
        cnx.close()
        cursor.close()
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Coin Leaderboard", style=ButtonStyle.green)
    async def coin_leaderboard(self, interaction: Interaction, _: ui.Button):
        cnx = connect(user="root", database="discord")
        cursor = cnx.cursor(buffered=True)
        cursor.execute(f'SELECT * FROM coins WHERE server="{interaction.guild.id}" ORDER BY coins DESC, gifted DESC LIMIT 10;')
        coins = cursor.fetchall()

        if coins == []:
            await interaction.response.edit_message("Nobody has used any betting commands.", ephemeral=True)
        description = ""
        index = 1
        for i in coins:
            user = await self.bot.fetch_user(i[0])
            if index == 1:
                description += f"**{index}.** 🥇 {user.display_name} - `{i[2]} coin{"s" if int(i[2]) != 1 else ""}`\n"
                imageUrl = user.display_avatar.url
            elif index == 2:
                description += f"**{index}.** 🥈 {user.display_name} - `{i[2]} coin{"s" if int(i[2]) != 1 else ""}`\n"
            elif index == 3:
                description += f"**{index}.** 🥉 {user.display_name} - `{i[2]} coin{"s" if int(i[2]) != 1 else ""}`\n"
            else:
                description += f"**{index}.** {user.display_name} - `{i[2]} coin{"s" if int(i[2]) != 1 else ""}`\n"
            index += 1
        embed = Embed(title="🏆 Top 10 Leaderboard", description=description, color = Color.from_rgb(200, 200, 0))
        embed.set_thumbnail(url=imageUrl)
        cursor.close()
        cnx.close()
        await interaction.response.edit_message(embed=embed, view=self)


class Gamble(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="bet", description="Bet QTC coins.")
    @app_commands.describe(
        amount="Amount of QTC coins to bet",
        side="The side of the coin you are betting on"
    )
    @app_commands.choices(side=[
        app_commands.Choice(name="Heads", value="Heads"),
        app_commands.Choice(name="Tails", value="Tails"),
        app_commands.Choice(name="Middle", value="Middle")
    ])
    async def bet(self, interaction: Interaction, amount: int, side:app_commands.Choice[str]="Heads"):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        if amount < 1:
            return await interaction.response.send_message("You must bet at least one coin.", ephemeral=True)

        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        cnx = connect(user="root", database="discord")
        cursor = cnx.cursor(buffered=True)
        # Fetch user coins
        cursor.execute(f'SELECT coins FROM coins WHERE user="{user_id}" AND server="{guild_id}";')
        row = cursor.fetchone()

        # If user not found, insert with 10 starting coins
        if row is None:
            cursor.execute(f'INSERT INTO coins(user, server, coins, gifted) VALUES("{user_id}", "{guild_id}", 10, 0);')
            coin_amount = 10
        else:
            coin_amount = int(row[0])

        # Handle 0 coins: reset to 1
        if coin_amount == 0:
            coin_amount = 1
            cursor.execute(f'UPDATE coins SET coins=1 WHERE user="{user_id}" AND server="{guild_id}";')
            if amount > 1:
                cnx.commit()
                return await interaction.response.send_message("You do not have enough coins. You have 1 coin.", ephemeral=True)

        # Not enough coins
        if amount > coin_amount:
            cnx.commit()
            return await interaction.response.send_message(f'You do not have enough coins. You have {coin_amount} coin{"s" if coin_amount != 1 else ""}.', ephemeral=True,)

        # Determine coin flip logic
        if coin_amount > 10:
            coin = choice(("Heads", "Tails"))
        elif coin_amount < 5:
            coin = side
        else:
            coin = choice(("Heads", "Heads", "Tails"))
        if randrange(0, 500) == 330:
            coin = "Middle"
        # coin = "Heads"
        # Update balance
        if side == "Heads":
                coin_amount += (amount * (2 * (coin == side) - 1))
        else:
                coin_amount += (amount * (2 * (coin == side.name) - 1))

        # Prevent 0 balance
        if coin == "Middle":
            if coin_amount == 0:
                coin_amount = 1
                result_msg = f"The coin landed in the middle (somehow), and you now have one coin. (Reset to one)"
            else:
                result_msg = f'The coin landed in the middle (somehow), and you now have {coin_amount} coin{"s" if coin_amount != 1 else ""}.'
        else:
            if coin_amount == 0:
                coin_amount = 1
                result_msg = f"The coin landed on {coin}, and you now have one coin. (Reset to one)"
            else:
                result_msg = f'The coin landed on {coin}, and you now have {coin_amount} coin{"s" if coin_amount != 1 else ""}.'

        # Commit new balance
        cursor.execute(f'UPDATE coins SET coins={coin_amount} WHERE user="{user_id}" AND server="{guild_id}";')

        cnx.commit()
        cnx.close()
        cursor.close()
        await interaction.response.send_message(result_msg)

    # @sus: 1054537051527188482
    # @fritbit: 947551947735576627
    # @concrete blocks: 1158108906405515285
    # @skibidi-bot: 1342990342999248936
    # ryans alt: 1324882449049583657

    @app_commands.command(name="gift", description="Gift QTC coins.")
    @app_commands.describe(
        amount="Amount of QTC coins to gift",
        member="Person to give QTC coins",
        reason="The reason for gifting the coins"
    )
    async def gift(self, interaction: Interaction, amount: int, member: Member, reason: str = None):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        giver_id = str(interaction.user.id)
        receiver_id = str(member.id)
        guild_id = str(interaction.guild.id)

        # Cannot gift to self
        if giver_id == receiver_id:
            return await interaction.response.send_message("You cannot gift yourself.", ephemeral=True)

        if amount < 1:
            return await interaction.response.send_message("You must gift at least one coin.", ephemeral=True)
        cnx = connect(user="root", database="discord")
        cursor = cnx.cursor(buffered=True)
        # Get giver's coins
        cursor.execute(f'SELECT * FROM coins WHERE user="{giver_id}" AND server="{guild_id}";')
        row = cursor.fetchall()

        if row == []:
            # If giver doesn't exist, give them 10 starter coins
            cursor.execute(f'INSERT INTO coins(user, server, coins, gifted) VALUES("{giver_id}", "{guild_id}", 10, 0);')
            #cnx.commit()
            giver_coins = 10
        else:
            giver_coins = int(row[0][2])
            giver_gifted = int(row[0][3])

        # Handle coin reset if 0
        if giver_coins == 0:
            cursor.execute(f'UPDATE coins SET coins=1 WHERE user="{giver_id}" AND server="{guild_id}";')
            giver_coins = 1

        # Not enough coins
        if amount > giver_coins:
            return await interaction.response.send_message(f"You do not have enough coins. You have {giver_coins} coin{'s' if giver_coins != 1 else ''}.", ephemeral=True,)

        # Prevent giving away all coins
        if amount == giver_coins:
            return await interaction.response.send_message(
                "You cannot gift all your coins.", ephemeral=True
            )

        # Deduct from giver
        updated_giver_coins = giver_coins - amount
        updated_giver_gifted = giver_gifted + amount
        cursor.execute(f'UPDATE coins SET coins={updated_giver_coins}, gifted={updated_giver_gifted} WHERE user="{giver_id}" AND server="{guild_id}";')

        # gift to receiver
        cursor.execute(f'SELECT coins FROM coins WHERE user="{receiver_id}" AND server="{guild_id}";')
        row = cursor.fetchone()

        if row is None:
            cursor.execute(f'INSERT INTO coins(user, server, coins, gifted) VALUES("{receiver_id}", "{guild_id}", {10 + amount}, 0);')
        else:
            receiver_coins = int(row[0]) + amount
            cursor.execute(f'UPDATE coins SET coins="{receiver_coins}" WHERE user="{receiver_id}" AND server="{guild_id}";')

        cnx.commit()
        cnx.close()
        cursor.close()
        await interaction.response.send_message(f"{interaction.user.mention} has gifted {member.mention} {amount} coin{'s' if amount != 1 else ''}{f" because of the reason: {reason}" if reason != None else ""}!",)

    @app_commands.command(
        name="leaderboard", description="Check the QTC coin leaderboard."
    )
    async def lb(self, interaction: Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        # Command
        cnx = connect(user="root", database="discord")
        cursor = cnx.cursor(buffered=True)
        cursor.execute(f'SELECT * FROM coins WHERE server="{interaction.guild.id}" ORDER BY coins DESC LIMIT 10;')
        coins = cursor.fetchall()
        if coins == []:
            await interaction.response.send_message("Nobody has used any betting commands.", ephemeral=True)
            return
        description = ""
        index = 1
        for i in coins:
            user = await self.bot.fetch_user(i[0])
            if index == 1:
                description += f"**{index}.** 🥇 {user.display_name} - `{i[2]} coin{"s" if int(i[2]) != 1 else ""}`\n"
                imageUrl = user.display_avatar.url
            elif index == 2:
                description += f"**{index}.** 🥈 {user.display_name} - `{i[2]} coin{"s" if int(i[2]) != 1 else ""}`\n"
            elif index == 3:
                description += f"**{index}.** 🥉 {user.display_name} - `{i[2]} coin{"s" if int(i[2]) != 1 else ""}`\n"
            else:
                description += f"**{index}.** {user.display_name} - `{i[2]} coin{"s" if int(i[2]) != 1 else ""}`\n"
            index += 1
        view = SimpleView(self.bot, interaction.guild.id)
        embed = Embed(title="🏆 Top 10 Leaderboard", description=description, color=Color.from_rgb(200, 200, 0))
        embed.set_thumbnail(url=imageUrl)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name="check-balance", description="Check the QTC coin balance of a user."
    )
    @app_commands.describe(member="Person to check the balance of")
    async def balance(self, interaction: Interaction, member: Member = None):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return
        cnx = connect(user="root", database="discord")
        cursor = cnx.cursor(buffered=True)
        # Command
        if member == None:
            member = interaction.user
        cursor.execute(f'SELECT * FROM coins WHERE user="{member.id}" AND server="{interaction.guild.id}";')
        coins = cursor.fetchall()
        if coins == []:
            cursor.execute(f'INSERT INTO coins(user, server, coins, gifted) VALUES("{member.id}", "{interaction.guild.id}", 10, 0)')
            cnx.commit()
            amount = 10
        else:
            amount = coins[0][2]
        if int(amount) == 0:
            amount = 1
            cursor.execute(f'UPDATE coins SET coins="1" WHERE user="{member.id}" AND server="{interaction.guild.id}";')
            cnx.commit()
        cursor.execute(
            'SELECT user, RANK() OVER (ORDER BY coins DESC, gifted DESC) AS `rank` '
            'FROM coins WHERE server = %s',
            (interaction.guild.id,)
        )
        rows = cursor.fetchall()
        for row in rows:
            if int(row[0]) == member.id:
                place1 = row[1]
                break
        cursor.execute(
            'SELECT user, RANK() OVER (ORDER BY gifted DESC, coins DESC) AS `rank` '
            'FROM coins WHERE server = %s',
            (interaction.guild.id,)
        )

        rows = cursor.fetchall()
        for row in rows:
            if int(row[0]) == member.id:
                place2 = row[1]
                break
        cursor.close()
        cnx.close()
        award1 = ""
        award2 = ""
        match place1:
            case 1:
                award1 = " 🥇"
            case 2:
                award1 = " 🥈"
            case 3:
                award1 = " 🥉"
        match place2:
            case 1:
                award2 = " 🥇"
            case 2:
                award2 = " 🥈"
            case 3:
                award2 = " 🥉"
        embed = Embed(
                    title=f"QTC Coin Balance of {member.display_name}",
                    description=f"{member.mention} has {amount} coin{"s" if int(amount) != 1 else ""}.\n\nPlace on Coin Leaderboard: {place1}{award1}\nPlace on Gift Leaderboard: {place2}{award2}",
                    color = Color.from_rgb(255, 255, 0)
                )
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Gamble(bot))
