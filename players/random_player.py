from tsuro import Player
from random import choice

class RandomPlayer(Player):
    def __init__(self):
        super().__init__()
        self.name += " - Random"

    def choose_action(self, state):
        return choice(state.actions())