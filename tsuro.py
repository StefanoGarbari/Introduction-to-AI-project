from dataclasses import dataclass
from tiles import TILES
import pygame

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

class State:
    def __init__(self, N=6):
        self.board : Board = [[None for _ in range(N)] for _ in range(N)]

    def follow_path(self, start: Position) -> tuple[Position, bool]:
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
        if i < 0 or i >= len(self.board) or j < 0 or j >= len(self.board[0]):
            return Position(i=i, j=j, entry=entry), False
        
        # check if the new position doesn't contain a tile
        if self.board[i][j] is None:
            return start, True
        

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


state = State()

# test tiles 
state.board[0][0] = PlacedTile(TILES[2], 0)
state.board[0][1] = PlacedTile(TILES[8], 2)
state.board[1][1] = PlacedTile(TILES[3], 2)
state.board[2][1] = PlacedTile(TILES[12], 3)
state.board[2][0] = PlacedTile(TILES[13], 1)

state.board[5][3] = PlacedTile(TILES[30], 3)
state.board[4][3] = PlacedTile(TILES[25], 3)
state.board[4][2] = PlacedTile(TILES[34], 0)

pos = state.follow_path(Position(0,-1,3))
print(pos)




###################### DEBUG GRAPHICS ########################
# chatgpt did this, i wanted to check if the board was working properly
###################### ############## ########################

pygame.init()
TILE_SIZE = 100
HEIGHT = len(state.board) * TILE_SIZE
WIDTH = len(state.board[0]) * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tile Board")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)

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

    for i in range(len(state.board)):
        for j in range(len(state.board[0])):
            rect = pygame.Rect(j*TILE_SIZE, i*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

            tile = state.board[i][j]
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