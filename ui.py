from tsuro import Position, Tile, PlacedTile
import pygame

TILE_SIZE = 100
HAND_AREA = 210
SIDE_PANEL_WIDTH = 500  # adjust as needed

COLORS = [
    (255, 0, 0),      # red
    (0, 150, 0),      # green
    (0, 0, 255),      # blue
    (255, 255, 0),    # yellow
    (255, 165, 0),    # orange
    (128, 0, 128),    # purple
    (255, 120, 180),  # pink
    (64, 224, 208),   # turquoise
]

BACKGROUND = (225, 191, 146)
TILE_COLOR = (139, 69, 19)
PATH_COLOR = (255, 255, 255)
CROWN_COLOR = (255, 215, 0)
BLACK = (0, 0, 0)

class TsuroUI:

    def __init__(self, board_width=6, board_height=6):
        pygame.init()

        self.board_width = board_width
        self.board_height = board_height

        self.width = board_width * TILE_SIZE + SIDE_PANEL_WIDTH
        self.height = board_height * TILE_SIZE + HAND_AREA

        self.board_pixel_width = board_width * TILE_SIZE
        self.board_pixel_height = board_height * TILE_SIZE

        self.font = pygame.font.SysFont(None, 24)
        self.font_big = pygame.font.SysFont(None, 35)

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tsuro")


    def draw_board(self, state):
        self.screen.fill(BACKGROUND)

        for i, row in enumerate(state.board):
            for j, tile in enumerate(row):

                rect = pygame.Rect(j*TILE_SIZE, i*TILE_SIZE, TILE_SIZE, TILE_SIZE)

                if tile:
                    self.draw_tile(tile, rect)
                else:
                    pygame.draw.rect(self.screen, TILE_COLOR, rect, 1)

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

        di, dj, entry = ENTRY_MAP[start.entry]
        i = start.i + di
        j = start.j + dj

        if i < 0 or i >= len(state.board) or j < 0 or j >= len(state.board[0]) or state.board[i][j] is None:
            pygame.draw.circle(self.screen, color, self.get_entry_point_rect(pygame.Rect(start.j*TILE_SIZE, start.i*TILE_SIZE, TILE_SIZE, TILE_SIZE), start.entry, 0), 7)
            return

        entry_rotated = entry - 2 * state.board[i][j].rotation
        if entry_rotated <= 0:
            entry_rotated += 8

        exit_rotated = state.board[i][j].tile[entry_rotated]

        exit = exit_rotated + 2 * state.board[i][j].rotation
        if exit > 8:
            exit -= 8

        rect = pygame.Rect(j*TILE_SIZE, i*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        p1 = self.get_entry_point_rect(rect, entry, 0)
        p2 = self.get_entry_point_rect(rect, exit, 0)
        t1 = self.get_entry_tangent(entry, TILE_SIZE)
        t2 = self.get_entry_tangent(exit, TILE_SIZE)
        self.draw_curve(self.screen, color, p1, t1, p2, t2)

        self.draw_path(state, Position(i=i, j=j, entry=exit), color)


    def rotate_entry(self, entry: int, rotation: int) -> int:
        return ((entry - 1 + 2 * rotation) % 8) + 1


    def get_entry_tangent(self, entry_rotated: int, S: int):
        """Return inward control-point offset for an already-rotated entry number."""
        d = S // 3
        if entry_rotated in (1, 2):   # bottom edge → inward is up
            return (0, -d)
        elif entry_rotated in (3, 4): # right edge → inward is left
            return (-d, 0)
        elif entry_rotated in (5, 6): # top edge → inward is down
            return (0, d)
        else:                         # left edge → inward is right
            return (d, 0)


    def draw_curve(self, surface, color, p1, t1, p2, t2, width: int = 3):
        """Draw a cubic Bézier curve from p1 to p2 using inward tangent offsets t1/t2."""
        cp1 = (p1[0] + t1[0], p1[1] + t1[1])
        cp2 = (p2[0] + t2[0], p2[1] + t2[1])
        points = []
        for k in range(21):
            t = k / 20
            mt = 1 - t
            x = mt**3*p1[0] + 3*mt**2*t*cp1[0] + 3*mt*t**2*cp2[0] + t**3*p2[0]
            y = mt**3*p1[1] + 3*mt**2*t*cp1[1] + 3*mt*t**2*cp2[1] + t**3*p2[1]
            points.append((x, y))
        pygame.draw.lines(surface, color, False, points, width)


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


    def draw_tile(self, tile: PlacedTile, rect: pygame.Rect, alpha: int = 255):
        if alpha == 255:
            pygame.draw.rect(self.screen, TILE_COLOR, rect)
            drawn = set()
            for a, b in tile.tile.items():
                if a in drawn:
                    continue
                p1 = self.get_entry_point_rect(rect, a, tile.rotation)
                p2 = self.get_entry_point_rect(rect, b, tile.rotation)
                t1 = self.get_entry_tangent(self.rotate_entry(a, tile.rotation), rect.width)
                t2 = self.get_entry_tangent(self.rotate_entry(b, tile.rotation), rect.width)
                self.draw_curve(self.screen, PATH_COLOR, p1, t1, p2, t2)
                drawn.add(a)
                drawn.add(b)
        else:
            surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            local_rect = pygame.Rect(0, 0, rect.width, rect.height)
            pygame.draw.rect(surface, (*TILE_COLOR, alpha), local_rect)
            drawn = set()
            path_color = (*PATH_COLOR, min(255, alpha + 60))
            for a, b in tile.tile.items():
                if a in drawn:
                    continue
                p1 = self.get_entry_point_rect(local_rect, a, tile.rotation)
                p2 = self.get_entry_point_rect(local_rect, b, tile.rotation)
                t1 = self.get_entry_tangent(self.rotate_entry(a, tile.rotation), local_rect.width)
                t2 = self.get_entry_tangent(self.rotate_entry(b, tile.rotation), local_rect.width)
                self.draw_curve(surface, path_color, p1, t1, p2, t2)
                drawn.add(a)
                drawn.add(b)
            self.screen.blit(surface, rect.topleft)


    def display_board(self, state):

        running = True

        while running:

            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_board(state)
            self.draw_all_hands(state)
            pygame.display.flip()

    def show_board(self, state):
        self.draw_board(state)
        self.draw_all_hands(state)
        pygame.display.flip()

    def ui_choose_tile(self, state, player):

        hand_with_rotation = [PlacedTile(tile, 0) for tile in player.hand]

        while True:

            self.clock.tick(60)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    x,y = pygame.mouse.get_pos()
                    result = self.handle_click(x, y, player.hand)

                    if result != -1:
                        if event.button == 1:   # LEFT CLICK
                            return hand_with_rotation[result]

                        elif event.button == 3: # RIGHT CLICK
                            r = (hand_with_rotation[result].rotation + 1) % 4
                            hand_with_rotation[result] = PlacedTile(hand_with_rotation[result].tile, r)


            self.draw_board(state)
            self.draw_all_hands(state)
            self.draw_hand(hand_with_rotation)

            # Draw hover preview on board
            mx, my = pygame.mouse.get_pos()
            hovered_idx = self.handle_click(mx, my, player.hand)
            if hovered_idx != -1:
                _, next_pos, in_bounds = state.follow_path(player.start)
                if in_bounds:
                    rect = pygame.Rect(next_pos.j * TILE_SIZE, next_pos.i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    self.draw_tile(hand_with_rotation[hovered_idx], rect, alpha=120)

            i = state.players.index(player)
            color = COLORS[i % len(COLORS)]
            text_surface = self.font_big.render(f"{player.name}, play a tile", True, color)
            text_rect = text_surface.get_rect(
                center=(self.board_pixel_width // 2, self.board_pixel_height + 30)
            )
            self.screen.blit(text_surface, text_rect)

            text_surface = self.font.render("Right click on a tile to rotate it", True, BLACK)
            text_rect = text_surface.get_rect(
                center=(self.board_pixel_width // 2, self.board_pixel_height + 185)
            )
            self.screen.blit(text_surface, text_rect)

            pygame.display.flip()

    def handle_click(self, x, y, hand):

        n = len(hand)
        if n == 0:
            return -1

        spacing = (self.width - SIDE_PANEL_WIDTH) // (n + 1)
        tile_y = self.board_pixel_height + 60

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

        spacing = (self.width - SIDE_PANEL_WIDTH) // (n + 1)
        y = self.board_pixel_height + 60

        for idx, tile in enumerate(hand):

            x = spacing * (idx + 1) - TILE_SIZE // 2
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            self.draw_tile(tile, rect)

    def draw_all_hands(self, state):

        players = state.players

        if not players:
            return

        panel_x = self.board_width * TILE_SIZE
        panel_width = self.width - panel_x

        row_height = TILE_SIZE + 30  # extra space for name
        total_height = len(players) * row_height + (len(players) - 1) * 10
        start_y = (self.board_pixel_height - total_height) // 2

        for i, player in enumerate(players):

            hand = player.hand
            color = COLORS[i % len(COLORS)]

            y = start_y + i * (row_height + 10)

            # --- draw name ---
            big = ((i == state.active_player) or (state.is_terminal() and state.is_player_alive(player)))
            font = self.font_big if big else self.font

            text_surface = font.render(player.name, True, color)

            text_rect = text_surface.get_rect(
                center=(panel_x + panel_width // 2, y + 5)
            )

            self.screen.blit(text_surface, text_rect)

            # --- draw crowns next to name ---

            if state.is_terminal() and state.is_player_alive(player):
                # crown points
                points = [
                    (0, 0),
                    (15, 15),
                    (30, 0),
                    (45, 15),
                    (60, 0),
                    (50, 30),
                    (10, 30),
                ]

                crown_x = text_rect.right + 5
                crown_y = text_rect.centery - 20
                pygame.draw.polygon(self.screen, CROWN_COLOR, [(x + crown_x, y + crown_y) for x, y in points])

                crown_x = text_rect.left - 65
                crown_y = text_rect.centery - 20
                pygame.draw.polygon(self.screen, CROWN_COLOR, [(x + crown_x, y + crown_y) for x, y in points])

            # --- draw hand below name ---
            hand_y = y + 20
            self.draw_hand_row([PlacedTile(tile, 0) for tile in hand], panel_x, panel_width, hand_y)

    def draw_hand_row(self, hand, panel_x, panel_width, y):

        n = len(hand)
        if n == 0:
            return

        spacing = panel_width // (n + 1)

        for idx, tile in enumerate(hand):

            x = panel_x + spacing * (idx + 1) - TILE_SIZE // 2
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            self.draw_tile(tile, rect)
