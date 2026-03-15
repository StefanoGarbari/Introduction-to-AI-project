from tsuro import Game
from players.random_player import RandomPlayer
from players.ui_player import UIPlayer
from players.mcts_ai_player import MCTSPlayer
from ui import TsuroUI
import time

ui = TsuroUI()

p1 = RandomPlayer()
p2 = MCTSPlayer()
game = Game([p1, p2])

try:
    game.play()
except Exception as e:
    print(f"Error occurred during game play: {e}")

ui.display_board(game.state)