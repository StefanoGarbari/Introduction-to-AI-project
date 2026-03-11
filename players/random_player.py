from tsuro import Player
from random import choice

class RandomPlayer(Player):
    def choose_action(self, state):
        return choice(state.actions())