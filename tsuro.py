from __future__ import annotations
from dataclasses import dataclass
from random import randrange
from tiles import TILES
from abc import ABC, abstractmethod
from enum import Enum

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

class ActionType(Enum):
    PLAY_TILE = 1
    DRAW_TILE = 2

@dataclass
class Action:
    type: ActionType
    player: int
    placed_tile: PlacedTile | None = None
    drawn_tile: Tile | None = None

class State:
    def __init__(self, players: list[Player], N=6):
        self.board : Board = [[None for _ in range(N)] for _ in range(N)]

        self.draw_pile : list[Tile] = [t for t in TILES]

        self.players = players
        for player in self.players:
            for _ in range(3):
                player.hand.append(self.draw_pile.pop(randrange(len(self.draw_pile))))

        self.active_player = 0
        self.has_played = False

    def copy(self) -> State:
        new_state = object.__new__(State)

        # new board structure, same tiles
        new_state.board = [row[:] for row in self.board]

        # new draw pile list, same tiles
        new_state.draw_pile = self.draw_pile[:]

        # copy players (same class, copied data)
        new_players = []
        for p in self.players:
            new_p = p.__class__.__new__(p.__class__)  # create instance of same subclass

            new_p.hand = p.hand[:]        # new list, same tiles
            new_p.start = p.start         # same position reference

            new_players.append(new_p)

        new_state.players = new_players

        new_state.active_player = self.active_player
        new_state.has_played = self.has_played

        return new_state

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

    def is_player_alive(self, player: Player) -> bool:
        return self.follow_path(player.start)[2]

    def is_terminal(self) -> bool:
        if sum(self.is_player_alive(p) for p in self.players) <= 1:
            return True
        if sum(len(p.hand) for p in self.players) == 0:
            return True
        return False

    def get_result(self, player: Player) -> float:
        return 1 if self.is_player_alive(player) else 0

    def apply(self, action: Action):
        if action.player != self.active_player:
            raise Exception("Illegal action! The player is not the active player!")

        player = self.players[action.player]

        if action.type == ActionType.DRAW_TILE:
            # player draws a new tile
            if self.draw_pile:
                tile = self.draw_pile.pop(randrange(len(self.draw_pile)))
                player.hand.append(tile)
                action.drawn_tile = tile

            # update next player
            # if all are dead, there is no active player
            if self.is_terminal():
                self.active_player = None
            else:
                i = (self.active_player+1) % len(self.players)
                # skip players who already lost
                while not self.is_player_alive(self.players[i]) or not self.players[i].hand:
                    i = (i+1) % len(self.players)
                self.active_player = i
            
            # new active player still has to play
            self.has_played = False

        if action.type == ActionType.PLAY_TILE:
            if action.placed_tile.tile not in player.hand:
                raise Exception("Illegal action! The tile is not in the hand of player!")

            # remove the tile from the player's hand
            player.hand.remove(action.placed_tile.tile)

            # place the tile on the board
            _, next_pos, _ = self.follow_path(player.start)
            self.board[next_pos.i][next_pos.j] = action.placed_tile

            # if any player was killed, put its tiles back in the draw pile
            for p in self.players:
                if not self.is_player_alive(p):
                    self.draw_pile.extend(p.hand)
                    p.hand.clear()
                    
            # active player has played
            self.has_played = True


    def results(self, action: Action) -> State:
        state = self.copy()
        state.apply(action)
        return state

    def actions(self) -> list[Action]:
        if self.active_player is None:
            return []

        if self.has_played:
            return [Action(ActionType.DRAW_TILE, self.active_player)]

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
                    legal_actions.append(Action(ActionType.PLAY_TILE, self.active_player, placed))
                else:
                    illegal_actions.append(Action(ActionType.PLAY_TILE, self.active_player, placed))

                # undo
                self.board[next_pos.i][next_pos.j] = None

        return legal_actions if legal_actions else illegal_actions
