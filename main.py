from tsuro import State, Player, Position
from players.random_player import RandomPlayer
from players.ui_player import UIPlayer
from players.mcts_ai_player import MCTSPlayer
from ui import TsuroUI
from random import randint


class Game:
    def __init__(self, players: list[Player]):
        self.state = State(players)
        self._winners_announced = False

    def play(self):
        # choose starting point at random for now
        height = len(self.state.board)
        width = len(self.state.board[0])

        used_positions = set()
        for player in self.state.players:
            while True:
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

                pos = Position(i, j, entry)

                if pos not in used_positions:
                    used_positions.add(pos)
                    player.start = pos
                    break

        # play in loop
        while not self.state.is_terminal():
            
            active_player = self.state.players[self.state.active_player]
            action = active_player.choose_action(self.state)
            self.state.apply(action) # place tile
            self.state.apply(self.state.actions()[0]) # draw tile
            ui.show_board(self.state)
        
                # announce winners exactly once (only for the real game loop)
        if not self._winners_announced and self.state.is_terminal():
            for i, p in enumerate(self.state.players):
                if self.state.is_player_alive(p):
                    print(f"Winner: {i}")
            self._winners_announced = True

ui = TsuroUI()

p1 = RandomPlayer()
p2 = MCTSPlayer()
game = Game([p1, p2])

try:
    game.play()
except Exception as e:
    print(f"Error occurred during game play: {e}")

ui.display_board(game.state)