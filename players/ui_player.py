from tsuro import Player, Action
from ui import tsuro_ui

class UIPlayer(Player):
    def choose_action(self, state):
        return Action(self, tsuro_ui.choose_tile(state, self.hand))