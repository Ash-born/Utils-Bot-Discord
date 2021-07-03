import discord
import asyncio
import random
from copy import deepcopy
from discord.ext import commands


class Morpion(commands.Cog):
    X = "X"
    O = "O"
    EMPTY = ""
    EMOJIES = {
        1: ":one:", 2: ":two:", 3: ":three:",
        4: ":four:", 5: ":five:", 6: ":six:",
        7: ":seven:", 8: ":eight:", 9: ":nine:",
        X: ":red_square:", O: ":blue_square:"
    }
    BOARD = [[*range(i, i + 3)] for i in range(1, 10, 3)]

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players_ingame = set()

    def check_victory(self, board: list, player: str):
        cross1 = cross2 = True
        free = 0
        for rc in range(3):
            if board[rc][0] == player and board[rc][1] == player and board[rc][2] == player:
                return True
            if board[0][rc] == player and board[1][rc] == player and board[2][rc] == player:
                return True

            if board[rc][rc] != player:
                cross1 = False
            if board[rc][2 - rc] != player:
                cross2 = False

            for y in range(3):
                if board[rc][y] not in (self.O, self.X):
                    free += 1

        if cross1 or cross2:
            return True

        if free > 0:
            return False
        else:
            return None

    def verify_message(self, message: discord.Message, player: discord.Member, board: list) -> bool:
        if player != message.author:
            return False

        move = message.content
        if len(move) < 1 or move < '1' or move > '9':
            return False

        move = int(move[0]) - 1
        x = move // 3
        y = move % 3
        if board[x][y] in (self.O, self.X):
            return False

        return True

    def set_player_move(self, board: list, player: str, pos: str):
        move = int(pos[0]) - 1
        x = move // 3
        y = move % 3
        board[x][y] = player

    def display_board(self, board: list) -> str:
        text = ""
        for x in range(3):
            text += "\n"
            for y in range(len(board[x])):
                emoji = self.EMOJIES[board[x][y]]
                text += emoji

        return text

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)

    @commands.command(name="morpion")
    async def start_game(self, ctx: commands.Context, member: discord.Member):
        if ctx.author == member:
            await ctx.send("Tu ne peux pas jouer contre toi-même.")
            return
        elif member.bot:
            await ctx.send("Tu ne peux pas jouer contre un bot.")
            return

        if ctx.author in self.players_ingame:
            await ctx.send("Vous avez déjà une partie en cours !")
            return
        elif member in self.players_ingame:
            await ctx.send("Votre adversaire a déjà une partie en cours !")
            return
        else:
            self.players_ingame.update((ctx.author, member))

        board = deepcopy(self.BOARD)
        await ctx.send(self.display_board(board))

        players = [(ctx.author, self.X), (member, self.O)]
        turn = random.randint(0, 1)
        current_player = players[turn]
        running = True
        while running:
            await ctx.send(f"{current_player[0].display_name}, votre tour !")
            try:
                msg = await self.bot.wait_for("message", check=lambda x: self.verify_message(x, current_player[0], board), timeout=10)
            except asyncio.TimeoutError:
                winner = players[not turn]
                text = f"""
Le joueur {current_player[0].display_name}({current_player[1]}) n'a pas répondu...
Le joueur {winner[0]}({winner[1]}) gagne la partie !"""

                await ctx.send(text)
                self.players_ingame.difference_update((ctx.author, member))
                break

            self.set_player_move(board, current_player[1], msg.content)
            await ctx.send(self.display_board(board))

            victory = self.check_victory(board, current_player[1])
            if victory:
                await ctx.send(f"Le joueur {current_player[0].display_name}({current_player[1]}) a gagné !")
                self.players_ingame.difference_update((ctx.author, member))
                running = False
            elif victory is None:
                await ctx.send("Égalité !")
                self.players_ingame.difference_update((ctx.author, member))
                running = False
            else:
                turn = not turn
                current_player = players[turn]


def setup(bot):
    bot.add_cog(Morpion(bot))
