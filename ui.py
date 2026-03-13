from tsuro import Position, Tile, PlacedTile
import pygame

TILE_SIZE = 100
HAND_AREA = 140

COLORS = [
    (255, 0, 0),      # red
    (0, 255, 0),      # green
    (0, 0, 255),      # blue
    (255, 255, 0),    # yellow
    (255, 165, 0),    # orange
    (128, 0, 128),    # purple
    (255, 120, 180),  # pink
    (64, 224, 208),   # turquoise
]

BACKGROUND = (225, 191, 146)
TILE_COLOR = (139,69,19)
PATH_COLOR = (255, 255, 255)

class TsuroUI:

    def __init__(self, board_width=6, board_height=6):
        pygame.init()

        self.board_width = board_width
        self.board_height = board_height

        self.width = board_width * TILE_SIZE
        self.height = board_height * TILE_SIZE + HAND_AREA

        self.board_pixel_height = board_height * TILE_SIZE

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game")


    def draw_board(self, state):
        self.screen.fill(BACKGROUND)

        for i,row in enumerate(state.board):
            for j,tile in enumerate(row):

                rect = pygame.Rect(
                    j*TILE_SIZE,
                    i*TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )

                if state.board[i][j]:
                    pygame.draw.rect(self.screen, TILE_COLOR, rect)
                else:
                    pygame.draw.rect(self.screen, TILE_COLOR, rect, 1)

                if tile:
                    self.draw_tile(i, j, tile)
        
        for i, p in enumerate(state.players):
            self.draw_path(state, p.start, COLORS[i%len(COLORS)])


    def draw_path(self, state, start, color):
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
        # check if the new position doesn't contain a tile
        if i < 0 or i >= len(state.board) or j < 0 or j >= len(state.board[0]) or state.board[i][j] is None:
            pygame.draw.circle(self.screen, color, self.get_entry_point(start.i, start.j, start.entry, 0), 7)
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
        
        
        p1 = self.get_entry_point(i, j, entry, 0)
        p2 = self.get_entry_point(i, j, exit, 0)

        pygame.draw.line(self.screen, color, p1, p2, 3)

        self.draw_path(state, Position(i=i, j=j, entry=exit), color)


    
    def rotate_entry(self, entry: int, rotation: int) -> int:
        """Rotate entry number 90° clockwise per rotation step."""
        return ((entry - 1 + 2 * rotation) % 8) + 1


    def get_entry_point(self, i: int, j: int, entry: int, rotation: int):
        """Return pixel coordinates of an entry point."""
        entry = self.rotate_entry(entry, rotation)

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


    def draw_tile(self, i, j, tile):

        drawn = set()

        for a,b in tile.tile.items():

            if a in drawn:
                continue

            p1 = self.get_entry_point(i,j,a,tile.rotation)
            p2 = self.get_entry_point(i,j,b,tile.rotation)

            pygame.draw.line(self.screen, PATH_COLOR, p1, p2, 3)

            drawn.add(a)
            drawn.add(b)


    def display_board(self, state):

        running = True

        while running:

            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_board(state)
            pygame.display.flip()

    def choose_tile(self, state, hand):

        hand_with_rotation = [PlacedTile(tile, 0) for tile in hand]

        while True:

            self.clock.tick(60)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    x,y = pygame.mouse.get_pos()
                    result = self.handle_click(x,y,hand)

                    if result != -1:
                        if event.button == 1:   # LEFT CLICK
                            return hand_with_rotation[result]

                        elif event.button == 3: # RIGHT CLICK
                            r = (hand_with_rotation[result].rotation + 1) % 4
                            hand_with_rotation[result] = PlacedTile(hand_with_rotation[result].tile, r)
                

            self.draw_board(state)
            self.draw_hand(hand_with_rotation)

            pygame.display.flip()

    def handle_click(self, x, y, hand):

        n = len(hand)
        if n == 0:
            return -1

        spacing = self.width // (n + 1)
        tile_y = self.board_pixel_height + 20

        for idx in range(n):

            tile_x = spacing * (idx + 1) - TILE_SIZE // 2

            rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

            if rect.collidepoint(x, y):
                return idx

        return -1

    def draw_hand(self, hand):

        n = len(hand)
        if n == 0:
            return

        spacing = self.width // (n + 1)
        y = self.board_pixel_height + 20

        for idx, tile in enumerate(hand):

            x = spacing * (idx + 1) - TILE_SIZE // 2

            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            pygame.draw.rect(self.screen, TILE_COLOR, rect)

            self.draw_tile_from_rect(tile, rect)

    def get_entry_point_rect(self, rect, entry, rotation):

        entry = self.rotate_entry(entry, rotation)

        x = rect.x
        y = rect.y
        S = rect.width

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
        
    def draw_tile_from_rect(self, tile: PlacedTile, rect):

        drawn = set()

        for a, b in tile.tile.items():

            if a in drawn:
                continue

            p1 = self.get_entry_point_rect(rect, a, tile.rotation)
            p2 = self.get_entry_point_rect(rect, b, tile.rotation)

            pygame.draw.line(self.screen, PATH_COLOR, p1, p2, 3)

            drawn.add(a)
            drawn.add(b)
