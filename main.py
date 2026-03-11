from tsuro import Game
from players.random_player import RandomPlayer
from players.ui_player import UIPlayer

p1 = RandomPlayer()
p2 = UIPlayer()
game = Game([p1, p2])
game.play()

