from tsuro import Game
from players.random_player import RandomPlayer
from players.ui_player import UIPlayer
from players.mcts_ai_player import MCTSPlayer
from ui import TsuroUI

ui = TsuroUI()

# Add player instances here (UIPlayer, MCTSPlayer, RandomPlayer) to set up the game
# Make the AI explore more options by increasing its time limit (e.g. MCTSPlayer(3) )

players = [
    UIPlayer(ui),
    MCTSPlayer(1),
]

game = Game(players, ui)

try:
    game.play()
except Exception as e:
    print(f"Error occurred during game play: {e}")
