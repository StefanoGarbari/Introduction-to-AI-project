from dataclasses import dataclass
from tiles import TILES

@dataclass(frozen=True)
class Position:
    i: int
    j: int
    entry: int

@dataclass(frozen=True)
class PlacedTile:
    tile: dict[int, int]
    rotation: int

Board = list[list[PlacedTile | None]]

board : Board = [[None for _ in range(6)] for _ in range(6)]


def follow_path(start: Position) -> tuple[Position, bool]:
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

    # check if the new position is outside of the board
    if i < 0 or i >= 6 or j < 0 or j >= 6:
        return Position(i=i, j=j, entry=entry), False
    
    # check if the new position doesn't contain a tile
    if board[i][j] is None:
        return start, True
    

    # rotate the entry point instead of the tile (easier)
    entry_rotated = entry - 2 * board[i][j].rotation
    if entry_rotated <= 0:
        entry_rotated += 8

    # follow tile path
    exit_rotated = board[i][j].tile[entry_rotated]

    # rotate back the exit
    exit = exit_rotated + 2 * board[i][j].rotation
    if exit > 8:
        exit -= 8

    return follow_path(Position(i=i, j=j, entry=exit))


# test tiles 
board[0][0] = PlacedTile(TILES[2], 0)
board[0][1] = PlacedTile(TILES[8], 2)
board[1][1] = PlacedTile(TILES[3], 2)
board[2][1] = PlacedTile(TILES[12], 3)
board[2][0] = PlacedTile(TILES[13], 1)

board[5][3] = PlacedTile(TILES[30], 3)
board[4][3] = PlacedTile(TILES[25], 3)
board[4][2] = PlacedTile(TILES[34], 0)

pos = follow_path(Position(0,-1,3))
print(pos)



