from __future__ import annotations
from dataclasses import dataclass
from random import shuffle, randint, choice
from tiles import TILES
import pygame
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class Position:
    i: int
    j: int
    entry: int

Tile = dict[int, int]

@dataclass(frozen=True)
class PlacedTile:
    tile: Tile
    rotation: int

class Player(ABC):
    def __init__(self):
        self.hand: list[Tile]= []
        self.start: Position= None

    @abstractmethod
    def choose_action(self, state: State) -> Action:
        """
        Play using this strategy
        """
        pass

Board = list[list[PlacedTile | None]]

@dataclass
class Action:
    player: Player
    placed_tile: PlacedTile

class State:
    def __init__(self, players: list[Player], N=6):
        self.board : Board = [[None for _ in range(N)] for _ in range(N)]

        self.draw_pile : list[Tile] = [t for t in TILES]
        shuffle(self.draw_pile)

        self.players = players
        for player in self.players:
            for _ in range(3):
                player.hand.append(self.draw_pile.pop())

        self.active_player = 0

    def follow_path(self, start: Position) -> tuple[Position, Position, bool]:
        # entry: (di, dj, new_entry)
        ENTRY_MAP = {
            1: (1, 0, 6),
            2: (1, 0, 5),
            3: (0, 1, 8),
            4: (0, 1, 7),
            5: (-1, 0, 2),
            6: (-1, 0, 1),
            7: (0, -1, 4),
            8: (0, -1, 3),
        }

        # calculate coordinates i,j of the next tile
        # calculate entry point of the next tile
        di, dj, entry = ENTRY_MAP[start.entry]
        i = start.i + di
        j = start.j + dj

        next_pos = Position(i=i, j=j, entry=entry)

        # check if the new position is outside of the board
        if i < 0 or i >= len(self.board) or j < 0 or j >= len(self.board[0]):
            return start, next_pos, False

        # check if the new position doesn't contain a tile
        if self.board[i][j] is None:
            return start, next_pos, True
        

        # rotate the entry point instead of the tile (easier)
        entry_rotated = entry - 2 * self.board[i][j].rotation
        if entry_rotated <= 0:
            entry_rotated += 8

        # follow tile path
        exit_rotated = self.board[i][j].tile[entry_rotated]

        # rotate back the exit
        exit = exit_rotated + 2 * self.board[i][j].rotation
        if exit > 8:
            exit -= 8

        return self.follow_path(Position(i=i, j=j, entry=exit))

    def is_player_alive(self, player: Player):
        return self.follow_path(player.start)[2]

    def apply(self, action: Action):
        # remove the tile from the player's hand
        action.player.hand.remove(action.placed_tile.tile)

        # place the tile on the board
        _, next_pos, _ = self.follow_path(action.player.start)
        self.board[next_pos.i][next_pos.j] = action.placed_tile

        # player draws a new tile
        if self.draw_pile:
            action.player.hand.append(self.draw_pile.pop())

        # if any player was killed, put its tiles back in the draw pile
        for p in self.players:
            if not self.is_player_alive(p):
                self.draw_pile.extend(p.hand)
                p.hand.clear()

        # update next player
        # if all are dead, there is no active player
        if all(not self.is_player_alive(p) for p in self.players):
            self.active_player = None
            return
        i = (self.active_player+1) % len(self.players)
        # skip players who already lost
        while not self.is_player_alive(self.players[i]):
            i = (i+1) % len(self.players)
        self.active_player = i

    def actions(self) -> list[Action]:
        p = self.players[self.active_player]

        # position where the tile will be placed
        _, next_pos, _ = self.follow_path(p.start)

        legal_actions = []
        illegal_actions = []

        for tile in p.hand:
            for rotation in range(4):
                placed = PlacedTile(tile, rotation)

                # simulate
                self.board[next_pos.i][next_pos.j] = placed
                if self.is_player_alive(p):
                    legal_actions.append(Action(p, placed))
                else:
                    illegal_actions.append(Action(p, placed))

                # undo
                self.board[next_pos.i][next_pos.j] = None

        return legal_actions if legal_actions else illegal_actions


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
            self.state.apply(action)




class RandomPlayer(Player):

    def choose_action(self, state):
        return choice(state.actions())

p1 = RandomPlayer()
p2 = RandomPlayer()
game = Game([p1, p2])
game.play()


###################### DEBUG GRAPHICS ########################
# chatgpt did this, i wanted to check if the board was working properly
###################### ############## ########################

pygame.init()
TILE_SIZE = 100
HEIGHT = len(game.state.board) * TILE_SIZE
WIDTH = len(game.state.board[0]) * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tile Board")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
RED = (255, 100, 0)

# ----------------------------
# Entry position calculation
# ----------------------------

def rotate_entry(entry: int, rotation: int) -> int:
    """Rotate entry number 90° clockwise per rotation step."""
    return ((entry - 1 + 2 * rotation) % 8) + 1


def get_entry_point(i: int, j: int, entry: int, rotation: int):
    """Return pixel coordinates of an entry point."""
    entry = rotate_entry(entry, rotation)

    x = j * TILE_SIZE
    y = i * TILE_SIZE
    S = TILE_SIZE

    if entry == 1:
        return (x + S//3, y + S)
    elif entry == 2:
        return (x + 2*S//3, y + S)
    elif entry == 3:
        return (x + S, y + 2*S//3)
    elif entry == 4:
        return (x + S, y + S//3)
    elif entry == 5:
        return (x + 2*S//3, y)
    elif entry == 6:
        return (x + S//3, y)
    elif entry == 7:
        return (x, y + S//3)
    elif entry == 8:
        return (x, y + 2*S//3)


# ----------------------------
# Drawing
# ----------------------------

def draw_board():
    screen.fill(WHITE)

    for i in range(len(game.state.board)):
        for j in range(len(game.state.board[0])):
            rect = pygame.Rect(j*TILE_SIZE, i*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

            tile = game.state.board[i][j]
            if tile:
                drawn = set()

                for a, b in tile.tile.items():
                    if a in drawn:
                        continue

                    p1 = get_entry_point(i, j, a, tile.rotation)
                    p2 = get_entry_point(i, j, b, tile.rotation)

                    pygame.draw.line(screen, BLUE, p1, p2, 3)

                    drawn.add(a)
                    drawn.add(b)
    
    def draw_path(state: State, start: Position):
        ENTRY_MAP = {
            1: (1, 0, 6),
            2: (1, 0, 5),
            3: (0, 1, 8),
            4: (0, 1, 7),
            5: (-1, 0, 2),
            6: (-1, 0, 1),
            7: (0, -1, 4),
            8: (0, -1, 3),
        }

        # calculate coordinates i,j of the next tile
        # calculate entry point of the next tile
        di, dj, entry = ENTRY_MAP[start.entry]
        i = start.i + di
        j = start.j + dj

        next_pos = Position(i=i, j=j, entry=entry)

        # check if the new position is outside of the board
        if i < 0 or i >= len(state.board) or j < 0 or j >= len(state.board[0]):
            return

        # check if the new position doesn't contain a tile
        if state.board[i][j] is None:
            return

        # rotate the entry point instead of the tile (easier)
        entry_rotated = entry - 2 * state.board[i][j].rotation
        if entry_rotated <= 0:
            entry_rotated += 8

        # follow tile path
        exit_rotated = state.board[i][j].tile[entry_rotated]

        # rotate back the exit
        exit = exit_rotated + 2 * state.board[i][j].rotation
        if exit > 8:
            exit -= 8
        
        
        p1 = get_entry_point(i, j, entry, 0)
        p2 = get_entry_point(i, j, exit, 0)

        pygame.draw.line(screen, RED, p1, p2, 3)

        draw_path(state, Position(i=i, j=j, entry=exit))

    for p in game.state.players:
        draw_path(game.state, p.start)
        

# ----------------------------
# Main loop
# ----------------------------

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_board()
    pygame.display.flip()

pygame.quit()