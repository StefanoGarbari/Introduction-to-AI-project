from tsuro import State, Player, Position
from players.random_player import RandomPlayer
from players.ui_player import UIPlayer
from players.mcts_ai_player import MCTSPlayer
from ui import TsuroUI
import time
from random import randint


class Game:
    def __init__(self, players: list[Player]):
        self.state = State(players)

    def play(self):
        # choose starting point at random for now
        height = len(self.state.board)
        width = len(self.state.board[0])
        for player in self.state.players:
            ran = randint(0, 2 * height + 2 * width - 1)

            if ran < width:                     # top edge
                i = -1
                j = ran
                entry = randint(1, 2)
            elif ran < width + height:          # right edge
                i = ran - width
                j = width
                entry = randint(7, 8)
            elif ran < 2 * width + height:      # bottom edge
                i = height
                j = ran - (width + height)
                entry = randint(5, 6)
            else:                               # left edge
                i = ran - (2 * width + height)
                j = -1
                entry = randint(3, 4)

            player.start = Position(i, j, entry)

        # play in loop
        while ( sum(self.state.is_player_alive(p) for p in self.state.players) >= 2 and
                sum(t is not None for row in self.state.board for t in row) < height * width -1 ):
            
            active_player = self.state.players[self.state.active_player]
            action = active_player.choose_action(self.state)
            self.state.apply(action) # place tile
            self.state.apply(self.state.actions()[0]) # draw tile
            ui.draw_board(self.state)


ui = TsuroUI()

p1 = RandomPlayer()
p2 = MCTSPlayer()
game = Game([p1, p2])

try:
    game.play()
except Exception as e:
    print(f"Error occurred during game play: {e}")

ui.display_board(game.state)