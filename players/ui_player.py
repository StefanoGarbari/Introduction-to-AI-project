from tsuro import Player, Action
from ui import TsuroUI

class UIPlayer(Player):
    def __init__(self, ui: TsuroUI):
        super().__init__()
        self.ui = ui

    def choose_action(self, state):
        return Action(self, self.ui.choose_tile(state, self.hand))