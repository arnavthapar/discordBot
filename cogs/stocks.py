from discord import Interaction, app_commands, Embed, Color
from discord.ext import commands, tasks
from mysql.connector import connect
from random import gauss, randrange, choice
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from discord import File

def db():
    return connect(user="root", database="discord")


def update_price(current: float) -> float:
    drift = 0.001
    volatility = 0.04
    shock = gauss(0, 1)
    change = drift + volatility * shock
    return round(max(1.0, current * (1 + change)), 2)


def price_arrow(prev, curr):
    if curr > prev:
        return "🟢"
    elif curr < prev:
        return "🔴"
    return "⚪"


class Stocks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.price_update.start()
        self.market_event.start()

    def cog_unload(self):
        self.price_update.cancel()
        self.market_event.cancel()

    @tasks.loop(minutes=10)
    async def price_update(self):
        cnx = db()
        cursor = cnx.cursor(buffered=True)
        cursor.execute("SELECT ticker, price FROM stocks")
        for ticker, price in cursor.fetchall():
            new_price = update_price(float(price))
            cursor.execute(
                "UPDATE stocks SET prev_price=price, price=%s WHERE ticker=%s",
                (new_price, ticker)
            )
            # Log to history
            cursor.execute(
                "INSERT INTO stock_history (ticker, price) VALUES (%s, %s)",
                (ticker, new_price)
            )
        cnx.commit()
        cnx.close()
        cursor.close()

    @tasks.loop(hours=1) # loop every hour
    async def market_event(self):
        if randrange(2) == 0:
            return
        cnx = db()
        cursor = cnx.cursor(buffered=True)
        cursor.execute("SELECT ticker, name, price FROM stocks")
        stocks = cursor.fetchall()
        ticker, _, price = choice(stocks)
        multiplier = choice((0.7, 1.5, 2, 0.5, 0.8, 1.2))

        new_price = round(max(1.0, float(price) * multiplier), 2)
        cursor.execute(
            "UPDATE stocks SET prev_price=price, price=%s WHERE ticker=%s",
            (new_price, ticker)
        )
        cnx.commit()
        cnx.close()
        cursor.close()

    @price_update.before_loop
    @market_event.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

    group = app_commands.Group(name="stocks", description="QTC stock market commands")

    @group.command(name="market", description="View all stocks and current prices.")
    async def market(self, interaction: Interaction):
        cnx = db()
        cursor = cnx.cursor(buffered=True)
        cursor.execute("SELECT ticker, name, price, prev_price FROM stocks ORDER BY ticker")
        rows = cursor.fetchall()
        cnx.close()
        cursor.close()

        description = ""
        for ticker, name, price, prev in rows:
            price, prev = float(price), float(prev)
            pct = ((price - prev) / prev) * 100
            arrow = price_arrow(prev, price)
            sign = "+" if pct >= 0 else ""
            description += (
                f"{arrow} **${ticker}** — {name}\n"
                f"　`{price:.2f} coins` ({sign}{pct:.1f}%)\n\n"
            )

        embed = Embed(title="Stock Market", description=description, color=Color.from_rgb(0, 180, 120))
        embed.set_footer(text="Prices update every 10 minutes")
        await interaction.response.send_message(embed=embed)
    @group.command(name="graph", description="Show the last 10 price points of a stock.")
    @app_commands.describe(ticker="Stock ticker (e.g. QTC)")
    async def graph(self, interaction: Interaction, ticker: str):
        if interaction.guild is None:
            return await interaction.response.send_message("Cannot use in DMs.", ephemeral=True)

        ticker = ticker.upper()

        cnx = db()
        cursor = cnx.cursor(buffered=True)

        # Check stock exists
        cursor.execute("SELECT name, price FROM stocks WHERE ticker=%s", (ticker,))
        stock = cursor.fetchone()
        if not stock:
            cnx.close()
            return await interaction.response.send_message(
                f"No stock with ticker `${ticker}`.", ephemeral=True
            )
        name = stock[0]

        # Fetch last 10 history points
        cursor.execute(
            "SELECT price, recorded_at FROM stock_history WHERE ticker=%s ORDER BY recorded_at DESC LIMIT 10",
            (ticker,)
        )
        rows = cursor.fetchall()
        cnx.close()
        cursor.close()

        if len(rows) < 2:
            return await interaction.response.send_message(
                f"Not enough history yet for `${ticker}`. Check back after a few price updates!",
                ephemeral=True
            )

        # Reverse so oldest to newest, left to right
        rows = list(reversed(rows))
        prices = [float(r[0]) for r in rows]
        times  = [r[1] for r in rows]

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("#2b2d31")
        ax.set_facecolor("#1e1f22")

        color = "#57f287" if prices[-1] >= prices[0] else "#ed4245"

        ax.plot(times, prices, color=color, linewidth=2.5, marker="o", markersize=5)
        ax.fill_between(times, prices, min(prices) * 0.995, alpha=0.15, color=color)

        # Axis styling
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        fig.autofmt_xdate()
        ax.tick_params(colors="white")
        ax.yaxis.set_tick_params(labelcolor="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#3f4147")

        ax.set_title(f"${ticker} — {name}", color="white", fontsize=14, pad=10)
        ax.set_ylabel("Price (coins)", color="#aaaaaa", fontsize=10)
        ax.set_xlabel("Time", color="#aaaaaa", fontsize=10)
        ax.grid(axis="y", color="#3f4147", linestyle="--", linewidth=0.7)

        # Put current price
        ax.annotate(
            f"{prices[-1]:.2f}",
            xy=(times[-1], prices[-1]),
            xytext=(8, 4), textcoords="offset points",
            color="white", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", fc="#3f4147", ec="none")
        )

        plt.tight_layout()

        # Save to buffer and send as a Discord file
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120)
        buf.seek(0)
        plt.close(fig)

        embed = Embed(
            title=f"📈 ${ticker} Price History",
            description=f"Last **{len(rows)}** price points",
            color=Color.from_rgb(87, 242, 135) if prices[-1] >= prices[0] else Color.from_rgb(237, 66, 69)
        )
        embed.set_image(url="attachment://graph.png")
        await interaction.response.send_message(
            embed=embed,
            file=File(buf, filename="graph.png")
        )
    @group.command(name="buy", description="Buy shares of a stock.")
    @app_commands.describe(ticker="Stock ticker (e.g. QTC)", shares="Number of shares to buy")
    async def buy(self, interaction: Interaction, ticker: str, shares: int):
        if interaction.guild is None:
            return await interaction.response.send_message("Cannot use in DMs.", ephemeral=True)
        if shares < 1:
            return await interaction.response.send_message("Must buy at least 1 share.", ephemeral=True)

        ticker = ticker.upper()
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)

        cnx = db()
        cursor = cnx.cursor(buffered=True)

        # Check stock exists
        cursor.execute("SELECT name, price FROM stocks WHERE ticker=%s", (ticker,))
        stock = cursor.fetchone()
        if not stock:
            cnx.close()
            return await interaction.response.send_message(
                f"No stock with ticker `${ticker}`. Use `/stocks market` to see available stocks.",
                ephemeral=True
            )
        name, price = stock[0], float(stock[1])
        cost = round(price * shares, 2)

        # Check coin balance
        cursor.execute(
            f'SELECT coins FROM coins WHERE user="{user_id}" AND server="{guild_id}"'
        )
        row = cursor.fetchone()
        if row is None:
            cursor.execute(f'INSERT INTO coins(user, server) VALUES("{user_id}", "{guild_id}")')
            balance = 10
        else:
            balance = int(row[0]) or 1

        if cost > balance:
            cnx.close()
            return await interaction.response.send_message(
                f"Not enough coins. That costs **{cost:.2f}** but you only have **{balance}**.",
                ephemeral=True
            )

        # Deduct coins
        cursor.execute(
            f'UPDATE coins SET coins=coins-{cost} WHERE user="{user_id}" AND server="{guild_id}"'
        )

        # Upsert portfolio with rolling avg buy price
        cursor.execute(
            "SELECT shares, avg_buy_price FROM portfolios WHERE user=%s AND server=%s AND ticker=%s",
            (user_id, guild_id, ticker)
        )
        existing = cursor.fetchone()
        if existing:
            old_shares, old_avg = int(existing[0]), float(existing[1])
            new_shares = old_shares + shares
            new_avg = round((old_avg * old_shares + price * shares) / new_shares, 4)
            cursor.execute(
                "UPDATE portfolios SET shares=%s, avg_buy_price=%s WHERE user=%s AND server=%s AND ticker=%s",
                (new_shares, new_avg, user_id, guild_id, ticker)
            )
        else:
            cursor.execute(
                "INSERT INTO portfolios(user, server, ticker, shares, avg_buy_price) VALUES(%s,%s,%s,%s,%s)",
                (user_id, guild_id, ticker, shares, price)
            )

        cnx.commit()
        cnx.close()
        cursor.close()

        embed = Embed(
            title="✅ Purchase Successful",
            description=(
                f"Bought **{shares} share{'s' if shares != 1 else ''}** of **${ticker}** ({name})\n"
                f"Price per share: `{price:.2f} coins`\n"
                f"Total cost: `{cost:.2f} coins`"
            ),
            color=Color.from_rgb(0, 200, 100)
        )
        await interaction.response.send_message(embed=embed)

    @group.command(name="sell", description="Sell shares of a stock.")
    @app_commands.describe(ticker="Stock ticker (e.g. QTC)", shares="Number of shares to sell")
    async def sell(self, interaction: Interaction, ticker: str, shares: int):
        if interaction.guild is None:
            return await interaction.response.send_message("Cannot use in DMs.", ephemeral=True)
        if shares < 1:
            return await interaction.response.send_message("Must sell at least 1 share.", ephemeral=True)

        ticker = ticker.upper()
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)

        cnx = db()
        cursor = cnx.cursor(buffered=True)

        cursor.execute("SELECT price FROM stocks WHERE ticker=%s", (ticker,))
        stock = cursor.fetchone()
        if not stock:
            cnx.close()
            return await interaction.response.send_message(f"No stock `${ticker}` found.", ephemeral=True)
        price = float(stock[0])

        cursor.execute(
            "SELECT shares, avg_buy_price FROM portfolios WHERE user=%s AND server=%s AND ticker=%s",
            (user_id, guild_id, ticker)
        )
        holding = cursor.fetchone()
        if not holding or int(holding[0]) < shares:
            cnx.close()
            owned = int(holding[0]) if holding else 0
            return await interaction.response.send_message(
                f"You only own **{owned} share{'s' if owned != 1 else ''}** of `${ticker}`.",
                ephemeral=True
            )

        old_shares, avg_buy = int(holding[0]), float(holding[1])
        proceeds = round(price * shares, 2)
        pnl = round((price - avg_buy) * shares, 2)
        pnl_str = f"+{pnl:.2f}" if pnl >= 0 else f"{pnl:.2f}"
        pnl_emoji = "📈" if pnl >= 0 else "📉"

        # Add coins back
        cursor.execute(
            f'UPDATE coins SET coins=coins+{proceeds} WHERE user="{user_id}" AND server="{guild_id}"'
        )

        # Update portfolio
        new_shares = old_shares - shares
        if new_shares == 0:
            cursor.execute(
                "DELETE FROM portfolios WHERE user=%s AND server=%s AND ticker=%s",
                (user_id, guild_id, ticker)
            )
        else:
            cursor.execute(
                "UPDATE portfolios SET shares=%s WHERE user=%s AND server=%s AND ticker=%s",
                (new_shares, user_id, guild_id, ticker)
            )

        cnx.commit()
        cnx.close()
        cursor.close()

        embed = Embed(
            title="💰 Sale Complete",
            description=(
                f"Sold **{shares} share{'s' if shares != 1 else ''}** of `${ticker}`\n"
                f"Proceeds: `{proceeds:.2f} coins`\n"
                f"{pnl_emoji} P&L: `{pnl_str} coins`"
            ),
            color=Color.from_rgb(0, 180, 255) if pnl >= 0 else Color.from_rgb(220, 60, 60)
        )
        await interaction.response.send_message(embed=embed)

    @group.command(name="portfolio", description="View your stock holdings.")
    async def portfolio(self, interaction: Interaction):
        if interaction.guild is None:
            return await interaction.response.send_message("Cannot use in DMs.", ephemeral=True)

        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)

        cnx = db()
        cursor = cnx.cursor(buffered=True)
        cursor.execute(
            """SELECT p.ticker, s.name, p.shares, p.avg_buy_price, s.price
               FROM portfolios p JOIN stocks s ON p.ticker=s.ticker
               WHERE p.user=%s AND p.server=%s
               ORDER BY p.ticker""",
            (user_id, guild_id)
        )
        holdings = cursor.fetchall()
        cnx.close()
        cursor.close()

        if not holdings:
            return await interaction.response.send_message(
                "You don't own any stocks. Use `/stocks market` to browse.", ephemeral=True
            )

        total_value = 0
        total_pnl = 0
        description = ""
        for ticker, name, shares, avg_buy, curr_price in holdings:
            shares = int(shares)
            avg_buy, curr_price = float(avg_buy), float(curr_price)
            value = curr_price * shares
            pnl = (curr_price - avg_buy) * shares
            total_value += value
            total_pnl += pnl
            pnl_str = f"+{pnl:.2f}" if pnl >= 0 else f"{pnl:.2f}"
            if pnl > 0:
                emoji = "🟢"
            elif pnl == 0:
                emoji = "🟡"
            else:
                emoji = "🔴"
            description += (
                f"{emoji} **${ticker}** — {name}\n"
                f"　{shares} share{'s' if shares != 1 else ''} @ avg `{avg_buy:.2f}` → now `{curr_price:.2f}`\n"
                f"　Value: `{value:.2f}` | P&L: `{pnl_str}`\n\n"
            )

        pnl_total_str = f"+{total_pnl:.2f}" if total_pnl >= 0 else f"{total_pnl:.2f}"
        embed = Embed(
            title=f"{interaction.user.display_name}'s Portfolio",
            description=description,
            color=Color.from_rgb(255, 200, 0)
        )
        embed.add_field(name="Total Value", value=f"`{total_value:.2f} coins`")
        embed.add_field(name="Total P&L", value=f"`{pnl_total_str} coins`")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stocks(bot))