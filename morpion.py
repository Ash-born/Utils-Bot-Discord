import discord
import asyncio
import random
from discord.ext import commands


class Morpion(commands.Cog):
    X = "X"
    O = "O"
    EMPTY = ""

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
                if board[rc][y] == self.EMPTY:
                    free += 1

        if cross1 or cross2:
            return True

        if free > 0:
            return False
        else:
            return None

    def verify_message(self, message: str, board: list) -> bool:
        pos = message.split()
        if len(pos) >= 2 and pos[0].isdigit() and pos[1].isdigit():
            x = int(pos[0])
            y = int(pos[1])
            if x < len(board) and y < len(board) and not board[x][y]:
                return True
        else:
            return False

    def set_player_move(self, board: list, player: str, pos: tuple):
        x = int(pos[0])
        y = int(pos[1])
        board[x][y] = player

    def display_board(self, board: list) -> str:
        text = ""
        for x in range(3):
            text += "\n"
            for y in range(len(board[x])):
                if board[x][y] == self.X:
                    text += ":red_square:"
                elif board[x][y] == self.O:
                    text += ":blue_square:"
                else:
                    text += ":black_large_square:"

        return text

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)

    @commands.command(name="morpion")
    async def start_game(self, ctx: commands.Context, member: discord.Member):
        if ctx.author in self.players_ingame:
            await ctx.send("Vous avez déjà une partie en cours !")
            return
        elif member in self.players_ingame:
            await ctx.send("Votre adversaire a déjà une partie en cours !")
            return
        else:
            self.players_ingame.update((ctx.author, member))

        def check(msg: discord.Message, player, board):
            return msg.author == player and self.verify_message(msg.content, board)

        board = [[self.EMPTY for i in range(3)] for j in range(3)]
        await ctx.send(self.display_board(board))

        players = [(ctx.author, self.X), (member, self.O)]
        turn = random.randint(0, 1)
        current_player = players[turn]
        running = True
        while running:
            await ctx.send(f"{current_player[0].display_name}, votre tour !")
            try:
                msg = await self.bot.wait_for("message", check=lambda x: check(x, current_player[0], board), timeout=10)
            except asyncio.TimeoutError:
                winner = players[not turn]
                await ctx.send(f"Le joueur {current_player[0].display_name}({current_player[1]}) n'a pas répondu... Le joueur {winner[0]}({winner[1]}) gagne la partie !")
                self.players_ingame.difference_update((ctx.author, member))
                break

            pos = msg.content.split()
            self.set_player_move(board, current_player[1], pos)
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
