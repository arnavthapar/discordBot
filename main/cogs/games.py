from discord import Interaction, app_commands, ui, Embed, ButtonStyle, File#, Color
from discord.ext import commands
from random import choice
from cogs.dictlist import di
from random import randint, sample
from copy import deepcopy
from io import BytesIO
from PIL import Image#, ImageDraw, ImageFont
from pathlib import Path

class LetterModal(ui.Modal, title="Guess a letter"):
    letter = ui.TextInput(
        label="Enter a single letter",
        max_length=1,
        placeholder="a-z",
        required=True
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: Interaction):
        guess = self.letter.value.lower()

        # Retrieve game by message ID
        game = self.view.games.get(interaction.message.id)
        if not game:
            await interaction.response.send_message("Game not found.", ephemeral=True)
            return

        # Check if this user is the player who started the game
        if interaction.user.id != game["player_id"]:
            await interaction.response.send_message("You're not allowed to play this game.", ephemeral=True)
            return

        word = game["word"]
        guessed = game["guessed"]
        display = game["display"]
        wrong = game["wrong"]
        add = ""

        # Game logic
        if guess in word and guess not in guessed:
            for i, letter in enumerate(word):
                if letter == guess:
                    display[i] = guess
            guessed.append(guess)
        elif guess not in word:
            wrong.append(guess)
        elif guess in guessed:
            add = "You already guessed that letter."
        else:
            guessed.append(guess)

        shown = "".join(display)
        hangman_stage = self.view.pics[min(len(wrong), len(self.view.pics) - 1)]
        description = f"{hangman_stage}\n\n`{shown}`\n\n{add}"
        embed = Embed(title="Hangman", description=description)

        # Check win/loss conditions
        if "-" not in display:
            embed.description += "\nYou won!"
            self.view.clear_items()
        elif len(wrong) >= len(self.view.pics) - 1:
            embed.description += f"\nYou lost! The word was **{word}**."
            self.view.clear_items()

        await interaction.response.edit_message(embed=embed, view=self.view)

class MineModal(ui.Modal, title="Guess a Space"):
    letter = ui.TextInput(
        label="Enter a row and column.",
        max_length=2,
        placeholder="a-i, 1-9 (ex. a1, b8, i9, g6)",
        required=True
    )

    def __init__(self, view):
        super().__init__()
        self.view = view
    async def checkWin(self, external, internal): #check if won
            for i in range(9):
                for j in range(9):
                    if external[i][j] == "#":
                        if internal[i][j] != "m": return False
            return True
    async def revealCoords(self, external, internal, x, y):
        # If mine -> game over
        if internal[x][y] == "m":
            external[x][y] = internal[x][y]
            return True

        # Reveal number or empty
        external[x][y] = internal[x][y]

        # If it's a blank (0), reveal neighbors
        if internal[x][y] == 0:
            for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(internal) and 0 <= ny < len(internal[0]) and external[nx][ny] == "#":
                    await self.revealCoords(external, internal, nx, ny)

        return False
    async def on_submit(self, interaction:Interaction):
        coords = self.letter.value.lower()

        # Retrieve game by message ID
        game = self.view.games.get(interaction.message.id)
        if not game:
            await interaction.response.send_message("Game not found.", ephemeral=True)
            return

        # Check if this user is the player who started the game
        if interaction.user.id != game["player_id"]:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return

        internal = game["board"]
        external = game["shown"]
        win = False
        lose = False
        extra = ""
        cy = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7, "i":8} #dictionary for y coordinates
        if len(coords) > 1 and (coords[0] in cy and (coords[1] in ["1", "2", "3", "4", "5", "6", "7", "8", "9"])):
            x = cy[coords[0]]
            y = int(coords[1]) - 1
            if external[x][y] == "#": lose = await self.revealCoords(external, internal, x, y) # Empty square, call function
            else: extra = "That square has already been revealed.\n" # This square has already been revealed
        else: extra = "Sorry, those coordinates don't make sense. \nPut a letter from a - i for the row, then a number from 1 - 9 for the column.\n"
        win = await self.checkWin(external, internal)
        '''
        colors = {
            "#": (70, 70, 70),
            "m": (220, 20, 60),
            1: (0, 128, 255),
            2: (0, 180, 0),
            3: (255, 50, 50),
            4: (0, 0, 180),
            5: (180, 0, 0),
            6: (0, 200, 200),
            7: (100, 100, 100),
            8: (200, 200, 200),
            0: (200, 200, 200)
        }

        # Rendering parameters
        cell_size = 40
        padding = 5
        font = ImageFont.load_default()

        width = len(external[0]) * cell_size
        height = len(external) * cell_size

        img = Image.new("RGB", (width, height), (50, 50, 50))
        draw = ImageDraw.Draw(img)

        for y, row in enumerate(external):
            for x, val in enumerate(row):
                x0 = x * cell_size
                y0 = y * cell_size
                color = colors.get(val, (255, 255, 255))
                draw.rectangle([x0, y0, x0 + cell_size, y0 + cell_size], fill=(30, 30, 30), outline=(80, 80, 80))
                if val != 0:
                    text = str(val) if val not in ["#", "m"] else "m" if val == "m" else " "
                    left, top, right, bottom = font.getbbox(text)

                    # Calculate width and height
                    text_w = right - left
                    text_h = bottom - top
                    draw.text((x0 + (cell_size - text_w) / 2, y0 + (cell_size - text_h) / 2), text, fill=color, font=font)

        # Save to memory
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        file = File(buffer, filename="minesweeper.png")
        embed = Embed(title="Minesweeper", color=Color.blurple())
        embed.set_image(url="attachment://minesweeper.png")
        '''
        board = "  1 2 3 4 5 6 7 8 9\na "
        for idx, i in enumerate(external):
            for x in i:
                if x == "m":
                    board += "💣 "
                else:
                    board += str(x) + " "
            if idx != 8:
                board += f"\n{chr(ord('b')+idx)} "
        embed = Embed(title="Minesweeper", description=f"```\n{board}```\n{extra}")

        # Check win/loss conditions
        if win:
            embed.description = f"```\n{board}```\n\nYou won!"
            self.view.clear_items()
        elif lose:
            embed.description = f"```\n{board}```\n\nYou lost!"
            self.view.clear_items()
        await interaction.response.edit_message(embed=embed, view=self.view)#, attachments=(file,))
class n2048Buttons(ui.View):
    def __init__(self, bot: commands.Bot, games:dict):
        super().__init__(timeout=None)
        self.bot = bot
        self.games = games

    @ui.button(label="↑", style=ButtonStyle.primary, custom_id="up")
    async def up(self, interaction:Interaction, _: ui.Button):
        await self.dir(interaction, "up")
    @ui.button(label="←", style=ButtonStyle.primary, custom_id="left")
    async def left(self, interaction:Interaction, _: ui.Button):
        await self.dir(interaction, "left")
    @ui.button(label="↓", style=ButtonStyle.primary, custom_id="down")
    async def down(self, interaction:Interaction, _: ui.Button):
        await self.dir(interaction, "down")
    @ui.button(label="→", style=ButtonStyle.primary, custom_id="right")
    async def right(self, interaction:Interaction, _: ui.Button):
        await self.dir(interaction, "right")
    async def dir(self, interaction:Interaction, direction:str):

        # Retrieve game by message ID
        game = self.games.get(interaction.message.id)
        if not game:
            await interaction.response.send_message("Game not found.", ephemeral=True)
            return

        # Check if this user is the player who started the game
        if interaction.user.id != game["player_id"]:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        num = game['game']
        num.check_events(direction)
        file = await num.print_area()
        embed = Embed(title="2048")
        embed.set_image(url="attachment://2048.png")

        # Check win/loss conditions
        if num.win and not num.large:
            embed.description = f"You won!"
            self.clear_items()
        elif num.lose:
            embed.description = f"You lost!"
            self.clear_items()
        await interaction.response.edit_message(embed=embed, attachments=[file], view=self)

class MinesweeperView(ui.View):
    def __init__(self, bot: commands.Bot, games, player_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.games = games
        self.player_id = player_id  # The user who started the game

    @ui.button(label="Guess a Space", style=ButtonStyle.primary, custom_id="guess_button")
    async def guess_button(self, interaction: Interaction, _: ui.Button):
        # Only the player who started the game can press this button
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return

        modal = MineModal(self)
        await interaction.response.send_modal(modal)

class HangmanView(ui.View):
    def __init__(self, bot: commands.Bot, games, pics, player_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.games = games
        self.pics = pics
        self.player_id = player_id  # The user who started the game

    @ui.button(label="Guess a Letter", style=ButtonStyle.primary, custom_id="guess_button")
    async def guess_button(self, interaction: Interaction, _: ui.Button):
        # Only the player who started the game can press this button
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return

        modal = LetterModal(self)
        await interaction.response.send_modal(modal)

class Games(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games = {}
        self.baseMines = [["#", "#", "#", "#", "#", "#", "#", "#", "#"], ["#", "#", "#", "#", "#", "#", "#", "#", "#"], ["#", "#", "#", "#", "#", "#", "#", "#", "#"], ["#", "#", "#", "#", "#", "#", "#", "#", "#"], ["#", "#", "#", "#", "#", "#", "#", "#", "#"], ["#", "#", "#", "#", "#", "#", "#", "#", "#"], ["#", "#", "#", "#", "#", "#", "#", "#", "#"], ["#", "#", "#", "#", "#", "#", "#", "#", "#"], ["#", "#", "#", "#", "#", "#", "#", "#", "#"]]
        self.pics = (
            "```\n  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========\n```",
            "```\n  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========\n```",
            "```\n  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========\n```",
            "```\n  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========\n```",
            "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========\n```",
            "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========\n```",
            "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n=========\n```"
        )

    group = app_commands.Group(name="games", description="Commands related to playing games")

    async def checkSurroundings(self, array, x, y):
        if array[x][y] == "m": return 0
        directions = [
            (-1, 0), (1, 0),  # up, down
            (0, -1), (0, 1),  # left, right
            (-1, -1), (-1, 1),  # upper-left, upper-right
            (1, -1), (1, 1)    # lower-left, lower-right
        ]

        answer = 0
        size_x = len(array)
        size_y = len(array[0])

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size_x and 0 <= ny < size_y:
                if array[nx][ny] == "m":
                    answer += 1

        return answer

    @group.command(name="hangman", description="Play hangman.")
    @app_commands.describe(word="Optional word to use")
    async def hangman(self, interaction: Interaction, word: str = None):
        if word is None:
            word = choice(di)
        word = word.lower()

        display = ["-" for _ in word]
        guessed = []
        wrong = []

        embed = Embed(
            title="Hangman",
            description=f"{self.pics[0]}\n\n`{''.join(display)}`"
        )

        # Create a view tied to the player
        view = HangmanView(self.bot, self.games, self.pics, player_id=interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
        sent_msg = await interaction.original_response()

        # Store the game data
        self.games[sent_msg.id] = {
            "word": word,
            "guessed": guessed,
            "display": display,
            "wrong": wrong,
            "player_id": interaction.user.id
        }
    @group.command(name="minesweeper", description="Play minesweeper.")
    async def minesweeper(self, interaction: Interaction):
        board = "  1 2 3 4 5 6 7 8 9\na "
        for idx, i in enumerate(self.baseMines):
            for l in i:
                board += l + " "
            if idx != 8:
                board += f"\n{chr(ord('a')+idx + 1)} "
        embed = Embed(
            title="Minesweeper",
            description=f"```\n{board}\n```"
        )
        view = MinesweeperView(self.bot, self.games, player_id=interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
        sent_msg = await interaction.original_response()
        counter = 10
        internal = deepcopy(self.baseMines)
        while counter > 0:
            x = randint(0, 8)
            y = randint(0, 8)
            if internal[x][y] != "m":
                internal[x][y] = "m"
                counter -= 1
        # Finish generating internal
        checked = 0
        for i in range(9):
            for j in range(9):
                if internal[i][j] != "m":
                    checked = await self.checkSurroundings(internal, i, j)
                    internal[i][j] = checked

        self.games[sent_msg.id] = {
            "board": internal,
            "shown": deepcopy(self.baseMines),
            "player_id": interaction.user.id
        }
    @group.command(name="2048", description="Play 2048.")
    @app_commands.describe(large="Ability to go over 2048", ones="Start off with ones, not twos and fours")
    async def numbers(self, interaction:Interaction, large:bool=False, ones:bool=False):
        game = num_game(large, ones)
        game.area[game.random()][game.random()] += game.num()
        view = n2048Buttons(self.bot, self.games)
        embed = Embed(title="2048")
        file = await game.print_area()
        embed.set_image(url="attachment://2048.png")
        await interaction.response.send_message(embed=embed, view=view, file=file)
        sent_msg = await interaction.original_response()
        self.games[sent_msg.id] = {
            "game":game,
            "player_id": interaction.user.id
        }

class num_game():
    def __init__(self, large:bool, one:bool):
        self.area = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.prev_area = ''
        self.large = large
        self.one = one
        self.lose = False
        self.win = False
        self.msg_image = ""
        self.msg_image_rect = ""
    async def print_area(self) -> File:
        cell_size = 121
        offset = 15
        grid = Image.open("./images/grid.png").convert("RGBA")

        # Create a new RGBA canvas based on grid size
        img = Image.new("RGBA", grid.size, (255, 255, 255, 255))
        img.paste(grid, (0, 0), grid)

        # Draw each tile
        for y, row in enumerate(self.area):
            for x, value in enumerate(row):
                if value != 0:
                    PROJECT_ROOT = Path(__file__).resolve().parents[1]   # .. (goes up from cogs/ to project/)
                    IMAGES_DIR = PROJECT_ROOT / "images"
                    tile_path = IMAGES_DIR / f"{value}.png"
                    if not tile_path.exists():
                        directory = IMAGES_DIR / f"{value}.webp"
                        tile = Image.open(directory).convert("RGBA")
                    else: tile = Image.open(tile_path)

                    tile = tile.resize((105, 105))
                    img.paste(tile, (offset + x * cell_size, offset + y * cell_size), tile)

        # Save to memory
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return File(buffer, filename="2048.png")
    def random(self) -> int:
        return randint(0, 3)
    def num(self) -> int:
        if not self.one:
            return sample((2, 4), k=1)[0]
        return 1
    def move(self, dir, test=False, area=""):
        row_num = 0
        match dir:
            case "left":
                if not test:
                    for row in self.area:
                        filtered = self.shift_and_merge(row)
                        self.area[row_num] = filtered
                        row_num += 1
                else:
                    for row in area:
                        filtered = self.shift_and_merge(row)
                        area[row_num] = filtered
                        row_num += 1
                    return area

            case "right":
                if not test:
                    for row in self.area:
                        filtered = self.shift_and_merge(row[::-1])
                        self.area[row_num][::-1] = filtered
                        row_num += 1
                else:
                    for row in area:
                        filtered = self.shift_and_merge(row[::-1])
                        area[row_num][::-1] = filtered
                        row_num += 1
                    return area

            case "up":
                if not test:
                    self.area = list(map(list, zip(*self.area)))
                    for row in self.area:
                        filtered = self.shift_and_merge(row)
                        self.area[row_num] = filtered
                        row_num += 1
                    self.area = list(map(list, zip(*self.area)))
                else:
                    area = list(map(list, zip(*area)))
                    for row in area:
                        filtered = self.shift_and_merge(row)
                        area[row_num] = filtered
                        row_num += 1
                    area = list(map(list, zip(*area)))
                    return area

            case "down":
                if not test:
                    self.area = list(map(list, zip(*self.area)))
                    for row in self.area:
                        filtered = self.shift_and_merge(row[::-1])
                        self.area[row_num][::-1] = filtered
                        row_num += 1
                    self.area = list(map(list, zip(*self.area)))
                else:
                    area = list(map(list, zip(*area)))
                    for row in area:
                        filtered = self.shift_and_merge(row[::-1])
                        area[row_num][::-1] = filtered
                        row_num += 1
                    area = list(map(list, zip(*area)))
                    return area
    def shift_and_merge(self, row):
        """Moves numbers left, merges them, then fills with zeros."""
        filtered = [num for num in row if num != 0]
        i = 0
        while i < len(filtered) - 1:
            if filtered[i] == filtered[i + 1]:
                filtered[i] += filtered[i]
                filtered.pop(i + 1)
            i += 1
        while len(filtered) < 4: filtered.append(0)
        return filtered

    def check_events(self, event):
        self.create = True
        moved = False
        self.prev_area = [row[:] for row in self.area]
        if not self.lose and not self.win:
            match event:
                case "left":
                    self.move("left")
                case "right":
                    self.move("right")
                case "up":
                    self.move("up")
                case "down":
                    self.move("down")
        if self.prev_area != self.area:
            moved = True
            found = False
            while found == False and moved == True:
                x = self.random()
                y = self.random()
                if self.area[x][y] == 0:
                    self.area[x][y] += self.num()
                    found = True
            zeros = False
            for i in self.area:
                for m in i:
                    if m == 2048:
                        self.win = True
                    elif m == 0:
                        zeros = True
                        break
            if not zeros:
                if self.move('left', True, self.area) == self.area:
                    if self.move('right', True, self.area) == self.area:
                        if self.move('up', True, self.area) == self.area:
                            if self.move('down', True, self.area) == self.area:
                                self.lose = True

async def setup(bot):
    await bot.add_cog(Games(bot))