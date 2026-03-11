from tsuro import Game
from players.random_player import RandomPlayer
from players.ui_player import UIPlayer
from ui import TsuroUI

ui = TsuroUI()

p1 = RandomPlayer()
p2 = UIPlayer(ui)
game = Game([p1, p2])
game.play()

ui.display_board(game.state)