"""
El Laberint de l'Anell d'Or
Part 1 of the 'El Senyor dels Anells' AI practice.

A 12x12 grid game where the player must collect rings in hierarchical order:
  - 6 bronze rings first
  - then 3 silver rings
  - then the 1 gold ring

Features:
  - A* pathfinding for HINT MODE (next best move) and GOD MODE (full path)
  - Barriers block movement through them
  - Player loses if cost exceeds min_cost + 5
"""

import pygame
import sys
import random
import heapq
from itertools import permutations

# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────
ROWS, COLS = 12, 12
CELL = 50
PANEL_W = 280          # right-side info panel width
WIN_W = COLS * CELL + PANEL_W
WIN_H = ROWS * CELL

FPS = 30

# Ring types
BRONZE = "bronze"
SILVER = "silver"
GOLD   = "gold"

RING_COUNTS = {BRONZE: 6, SILVER: 3, GOLD: 1}

# Barrier specs: (length,) tuples
BARRIER_SPECS = [5, 4, 3, 3, 3]

# Colours
C_BG         = (30,  30,  30)
C_GRID       = (60,  60,  60)
C_BARRIER    = (80,  80,  80)
C_PLAYER     = (50, 100, 220)
C_BRONZE     = (180, 100,  20)
C_SILVER     = (180, 180, 190)
C_GOLD       = (230, 200,  10)
C_PATH       = (0,  180,  80, 120)   # semi-transparent green overlay
C_HINT       = (255, 230,   0, 160)  # next-cell hint yellow
C_PANEL      = (20,  20,  20)
C_TEXT       = (220, 220, 220)
C_BTN        = (60,  80, 120)
C_BTN_H      = (80, 120, 180)
C_BTN_ACTIVE = (50, 160,  80)
C_WIN        = (30, 180,  30)
C_LOSE       = (200,  30,  30)

DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]


# ─────────────────────────────────────────────
#  Helper: Manhattan distance
# ─────────────────────────────────────────────
def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


# ─────────────────────────────────────────────
#  Minimum path through a set of targets from a start (nearest-neighbour + MST lower bound)
#  Used inside the A* heuristic.
# ─────────────────────────────────────────────
def min_path_through(start, targets):
    """
    Lower-bound estimate of the cost to visit all targets starting from 'start'.
    Uses the minimum spanning tree of the target set plus the distance from start
    to the nearest target. This is admissible because actual movement >= Manhattan.
    For small sets (<=5 targets) we use exact permutations.
    """
    if not targets:
        return 0
    targets = list(targets)
    if len(targets) == 1:
        return manhattan(start, targets[0])
    # For <=5 we can brute-force the shortest path order
    if len(targets) <= 5:
        best = float('inf')
        for perm in permutations(targets):
            cost = manhattan(start, perm[0])
            for i in range(len(perm)-1):
                cost += manhattan(perm[i], perm[i+1])
            best = min(best, cost)
        return best
    # Otherwise: MST heuristic
    # Prim's MST on all points (start + targets)
    points = [start] + targets
    n = len(points)
    in_mst = [False]*n
    min_edge = [float('inf')]*n
    min_edge[0] = 0
    total = 0
    for _ in range(n):
        # pick the node not in MST with smallest min_edge
        u = min((i for i in range(n) if not in_mst[i]), key=lambda i: min_edge[i])
        in_mst[u] = True
        total += min_edge[u]
        for v in range(n):
            if not in_mst[v]:
                d = manhattan(points[u], points[v])
                if d < min_edge[v]:
                    min_edge[v] = d
    return total


# ─────────────────────────────────────────────
#  Game state generation
# ─────────────────────────────────────────────
def generate_barriers(specs):
    """
    Generate barrier cells.  Each barrier is a line of consecutive cells in one
    of three orientations (horizontal / vertical / diagonal ↘).
    Returns list of sets, each set being the barrier's cells.
    """
    occupied = set()
    barriers = []
    orientations = [(0, 1), (1, 0), (1, 1)]   # horiz, vert, diag
    for length in specs:
        placed = False
        attempts = 0
        while not placed and attempts < 2000:
            attempts += 1
            dr, dc = random.choice(orientations)
            # Choose a valid start
            max_r = ROWS - dr*(length-1) - 1
            max_c = COLS - dc*(length-1) - 1
            if max_r < 0 or max_c < 0:
                continue
            r0 = random.randint(0, max_r)
            c0 = random.randint(0, max_c)
            cells = frozenset((r0 + dr*i, c0 + dc*i) for i in range(length))
            if cells & occupied:   # overlap with existing barrier
                continue
            occupied |= cells
            barriers.append(cells)
            placed = True
        if not placed:
            # Fallback: place a single cell barrier somewhere free
            for r in range(ROWS):
                for c in range(COLS):
                    if (r, c) not in occupied:
                        barriers.append(frozenset([(r, c)]))
                        occupied.add((r, c))
                        break
    return barriers


def generate_rings(barriers_cells):
    """Place rings on free cells."""
    occupied = set(barriers_cells)
    all_cells = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) not in occupied]
    random.shuffle(all_cells)
    rings = {}  # cell -> type
    idx = 0
    for rtype, count in [(BRONZE, 6), (SILVER, 3), (GOLD, 1)]:
        for _ in range(count):
            rings[all_cells[idx]] = rtype
            idx += 1
    return rings


def place_player(barriers_cells, rings):
    occupied = set(barriers_cells) | set(rings.keys())
    free = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) not in occupied]
    return random.choice(free)


# ─────────────────────────────────────────────
#  A* search
# ─────────────────────────────────────────────
def astar(start_pos, start_collected, rings_dict, barriers_set):
    """
    A* to find the minimum-cost path from (start_pos, start_collected)
    to the state where all rings are collected (gold last).

    State: (player_row, player_col, frozenset_of_collected_ring_positions)
    Returns: (total_cost, list_of_positions) or (inf, []) if no path.
    """
    all_ring_positions = frozenset(rings_dict.keys())
    goal_collected = all_ring_positions

    def current_tier(collected):
        bronze_pos = frozenset(p for p, t in rings_dict.items() if t == BRONZE)
        silver_pos = frozenset(p for p, t in rings_dict.items() if t == SILVER)
        if not bronze_pos <= collected:
            return BRONZE, bronze_pos - collected
        if not silver_pos <= collected:
            return SILVER, silver_pos - collected
        gold_pos = frozenset(p for p, t in rings_dict.items() if t == GOLD)
        return GOLD, gold_pos - collected

    def heuristic(pos, collected):
        if collected == goal_collected:
            return 0
        # Remaining rings in order
        remaining_bronze = frozenset(p for p, t in rings_dict.items() if t == BRONZE and p not in collected)
        remaining_silver = frozenset(p for p, t in rings_dict.items() if t == SILVER and p not in collected)
        remaining_gold   = frozenset(p for p, t in rings_dict.items() if t == GOLD   and p not in collected)

        h = 0
        cur = pos
        # Must collect bronze first if any remain
        if remaining_bronze:
            cost_b = min_path_through(cur, remaining_bronze)
            h += cost_b
            # After bronze, move to some bronze end — approximate with MST already handles it
            # For chaining, use nearest neighbour greedy to get an endpoint estimate
            if remaining_bronze:
                # find approximate end position after collecting all bronze
                # use nearest-neighbour to get end
                cur = _nn_endpoint(cur, remaining_bronze)
        if remaining_silver:
            cost_s = min_path_through(cur, remaining_silver)
            h += cost_s
            cur = _nn_endpoint(cur, remaining_silver)
        if remaining_gold:
            h += min_path_through(cur, remaining_gold)
        return h

    def _nn_endpoint(start, targets):
        remaining = set(targets)
        pos = start
        while remaining:
            nearest = min(remaining, key=lambda t: manhattan(pos, t))
            pos = nearest
            remaining.remove(nearest)
        return pos

    # (f, g, pos, collected, path)
    start_state = (start_pos, frozenset(start_collected))
    g0 = 0
    h0 = heuristic(start_pos, frozenset(start_collected))
    heap = [(g0 + h0, g0, start_pos, frozenset(start_collected), [start_pos])]
    visited = {}  # (pos, collected) -> best g

    while heap:
        f, g, pos, collected, path = heapq.heappop(heap)
        state_key = (pos, collected)
        if state_key in visited and visited[state_key] <= g:
            continue
        visited[state_key] = g

        if collected == goal_collected:
            return g, path

        r, c = pos
        # Determine which rings are currently collectible
        _, next_tier_remaining = current_tier(collected)

        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            if (nr, nc) in barriers_set:
                continue
            new_g = g + 1
            new_collected = set(collected)
            if (nr, nc) in rings_dict:
                rtype = rings_dict[(nr, nc)]
                # Check if collectible
                bronze_done = all(p in new_collected for p, t in rings_dict.items() if t == BRONZE)
                silver_done = all(p in new_collected for p, t in rings_dict.items() if t == SILVER)
                can_collect = (
                    rtype == BRONZE or
                    (rtype == SILVER and bronze_done) or
                    (rtype == GOLD and bronze_done and silver_done)
                )
                if can_collect:
                    new_collected.add((nr, nc))
            new_collected = frozenset(new_collected)
            new_key = ((nr, nc), new_collected)
            if new_key in visited and visited[new_key] <= new_g:
                continue
            h = heuristic((nr, nc), new_collected)
            new_f = new_g + h
            heapq.heappush(heap, (new_f, new_g, (nr, nc), new_collected, path + [(nr, nc)]))

    return float('inf'), []


# ─────────────────────────────────────────────
#  Button helper
# ─────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, active_color=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.active_color = active_color or C_BTN_ACTIVE
        self.active = False

    def draw(self, surf, font):
        color = self.active_color if self.active else C_BTN
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        pygame.draw.rect(surf, C_TEXT, self.rect, 1, border_radius=6)
        txt = font.render(self.label, True, C_TEXT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ─────────────────────────────────────────────
#  Main game class
# ─────────────────────────────────────────────
class LaberintGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("El Laberint de l'Anell d'Or")
        self.clock = pygame.time.Clock()
        self.font_sm = pygame.font.SysFont("monospace", 14)
        self.font_md = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_lg = pygame.font.SysFont("monospace", 20, bold=True)
        self.font_xl = pygame.font.SysFont("monospace", 26, bold=True)

        # Overlay surface for transparent path highlights
        self.overlay = pygame.Surface((COLS*CELL, ROWS*CELL), pygame.SRCALPHA)

        self._init_buttons()
        self.new_game()

    def _init_buttons(self):
        px = COLS*CELL + 20
        bw, bh = PANEL_W - 40, 36
        self.btn_hint  = Button((px, 260, bw, bh), "HINT MODE")
        self.btn_god   = Button((px, 310, bw, bh), "GOD MODE")
        self.btn_reset = Button((px, 380, bw, bh), "RESET", C_BTN)

    def new_game(self):
        self.barriers = generate_barriers(BARRIER_SPECS)
        self.barriers_set = set()
        for b in self.barriers:
            self.barriers_set |= b

        self.rings = generate_rings(self.barriers_set)
        self.player = place_player(self.barriers_set, self.rings)
        self.collected = set()

        # Compute the global minimum cost from start
        self._recompute_min_cost()

        self.current_cost = 0
        self.game_over = False
        self.won = False
        self.hint_cell = None
        self.god_path = []
        self.btn_hint.active = False
        self.btn_god.active  = False
        self.message = ""

    def _recompute_min_cost(self):
        """Recompute min cost from current player position."""
        cost, path = astar(self.player, self.collected, self.rings, self.barriers_set)
        self.min_cost_from_start = cost if cost != float('inf') else 9999

    def _current_tier_remaining(self):
        bronze_remaining = [p for p, t in self.rings.items() if t == BRONZE and p not in self.collected]
        silver_remaining = [p for p, t in self.rings.items() if t == SILVER and p not in self.collected]
        gold_remaining   = [p for p, t in self.rings.items() if t == GOLD   and p not in self.collected]
        if bronze_remaining:
            return BRONZE, bronze_remaining
        if silver_remaining:
            return SILVER, silver_remaining
        return GOLD, gold_remaining

    def _try_collect(self):
        """Try to collect ring at current player position."""
        if self.player in self.rings and self.player not in self.collected:
            rtype = self.rings[self.player]
            bronze_done = all(p in self.collected for p, t in self.rings.items() if t == BRONZE)
            silver_done = all(p in self.collected for p, t in self.rings.items() if t == SILVER)
            can = (
                rtype == BRONZE or
                (rtype == SILVER and bronze_done) or
                (rtype == GOLD and bronze_done and silver_done)
            )
            if can:
                self.collected.add(self.player)
                if rtype == GOLD:
                    self.won = True
                    self.game_over = True
                    self.message = "HAS GUANYAT!"
            else:
                tier_name = "bronze" if not bronze_done else "plata"
                self.message = f"Necessites recollir primer els anells de {tier_name}!"

    def move(self, dr, dc):
        if self.game_over:
            return
        nr, nc = self.player[0]+dr, self.player[1]+dc
        if not (0 <= nr < ROWS and 0 <= nc < COLS):
            return
        if (nr, nc) in self.barriers_set:
            self.message = "Camí bloquejat per una barrera!"
            return
        self.player = (nr, nc)
        self.current_cost += 1
        self.message = ""
        self._try_collect()
        if not self.game_over:
            # Check lose condition
            if self.current_cost > self.min_cost_from_start + 5:
                self.game_over = True
                self.won = False
                self.message = "HAS PERDUT! Massa passos."
        # Invalidate hint/god if active
        if self.btn_hint.active:
            self._compute_hint()
        if self.btn_god.active:
            self._compute_god()

    def _compute_hint(self):
        cost, path = astar(self.player, self.collected, self.rings, self.barriers_set)
        if len(path) >= 2:
            self.hint_cell = path[1]
        else:
            self.hint_cell = None

    def _compute_god(self):
        cost, path = astar(self.player, self.collected, self.rings, self.barriers_set)
        self.god_path = path[1:] if len(path) >= 2 else []

    def toggle_hint(self):
        self.btn_hint.active = not self.btn_hint.active
        self.btn_god.active = False
        self.god_path = []
        if self.btn_hint.active:
            self._compute_hint()
        else:
            self.hint_cell = None

    def toggle_god(self):
        self.btn_god.active = not self.btn_god.active
        self.btn_hint.active = False
        self.hint_cell = None
        if self.btn_god.active:
            self._compute_god()
        else:
            self.god_path = []

    # ── Drawing ──────────────────────────────
    def draw(self):
        self.screen.fill(C_BG)
        self.overlay.fill((0, 0, 0, 0))

        # God mode path
        if self.btn_god.active:
            for (r, c) in self.god_path:
                self.overlay.fill(C_PATH, (c*CELL, r*CELL, CELL, CELL))

        # Hint mode next cell
        if self.btn_hint.active and self.hint_cell:
            r, c = self.hint_cell
            self.overlay.fill(C_HINT, (c*CELL, r*CELL, CELL, CELL))

        self.screen.blit(self.overlay, (0, 0))

        # Grid lines
        for r in range(ROWS+1):
            pygame.draw.line(self.screen, C_GRID, (0, r*CELL), (COLS*CELL, r*CELL))
        for c in range(COLS+1):
            pygame.draw.line(self.screen, C_GRID, (c*CELL, 0), (c*CELL, ROWS*CELL))

        # Barriers
        for cell in self.barriers_set:
            r, c = cell
            pygame.draw.rect(self.screen, C_BARRIER, (c*CELL+1, r*CELL+1, CELL-2, CELL-2))

        # Rings
        for pos, rtype in self.rings.items():
            if pos in self.collected:
                continue
            r, c = pos
            cx, cy = c*CELL + CELL//2, r*CELL + CELL//2
            color = {BRONZE: C_BRONZE, SILVER: C_SILVER, GOLD: C_GOLD}[rtype]
            pygame.draw.circle(self.screen, color, (cx, cy), CELL//2 - 6)
            pygame.draw.circle(self.screen, C_BG, (cx, cy), CELL//2 - 14)  # ring hole

        # Player
        pr, pc = self.player
        cx, cy = pc*CELL + CELL//2, pr*CELL + CELL//2
        pygame.draw.circle(self.screen, C_PLAYER, (cx, cy), CELL//2 - 8)

        # Panel
        self._draw_panel()

        # Game-over overlay
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_panel(self):
        px = COLS*CELL
        pygame.draw.rect(self.screen, C_PANEL, (px, 0, PANEL_W, WIN_H))
        pygame.draw.line(self.screen, C_GRID, (px, 0), (px, WIN_H), 2)

        x = px + 14
        y = 16
        title = self.font_lg.render("ANELL D'OR", True, C_GOLD)
        self.screen.blit(title, (px + (PANEL_W - title.get_width())//2, y))
        y += 36

        # Score info
        tier, rem = self._current_tier_remaining()
        lines = [
            f"Posicio: ({self.player[0]},{self.player[1]})",
            f"Cost actual: {self.current_cost}",
            f"Cost minim*: {self.min_cost_from_start}",
            f"Limit: {self.min_cost_from_start + 5}",
            "",
            f"Anells de bronze:  {sum(1 for p,t in self.rings.items() if t==BRONZE and p in self.collected)}/6",
            f"Anells de plata:   {sum(1 for p,t in self.rings.items() if t==SILVER and p in self.collected)}/3",
            f"Anell d'or:        {sum(1 for p,t in self.rings.items() if t==GOLD   and p in self.collected)}/1",
            "",
            f"Objectiu actual: {tier.upper()}",
            f"Restants: {len(rem)}",
        ]
        for line in lines:
            surf = self.font_sm.render(line, True, C_TEXT)
            self.screen.blit(surf, (x, y))
            y += 18
        y += 8

        # Buttons
        for btn in [self.btn_hint, self.btn_god, self.btn_reset]:
            btn.rect.y = y
            btn.rect.x = px + 20
            btn.rect.width = PANEL_W - 40
            btn.draw(self.screen, self.font_md)
            y += 50

        # Legend
        y += 6
        legend = self.font_sm.render("Llegenda:", True, C_TEXT)
        self.screen.blit(legend, (x, y)); y += 20
        for color, label in [(C_BRONZE,"Bronze"),(C_SILVER,"Plata"),(C_GOLD,"Or"),(C_PLAYER,"Jugador"),(C_BARRIER,"Barrera")]:
            pygame.draw.circle(self.screen, color, (x+8, y+8), 8)
            txt = self.font_sm.render(label, True, C_TEXT)
            self.screen.blit(txt, (x+22, y))
            y += 22

        # Controls
        y += 8
        for line in ["Controls:", "Fletxes / WASD / numpad", "per moure's"]:
            surf = self.font_sm.render(line, True, (150,150,150))
            self.screen.blit(surf, (x, y)); y += 16

        # Message
        if self.message:
            msg_surf = self.font_sm.render(self.message[:32], True, (255, 180, 50))
            self.screen.blit(msg_surf, (px + 10, WIN_H - 30))

        # * footnote
        note = self.font_sm.render("* des de l'inici del joc", True, (100,100,100))
        self.screen.blit(note, (px + 10, WIN_H - 14))

    def _draw_game_over(self):
        s = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.screen.blit(s, (0, 0))
        color = C_WIN if self.won else C_LOSE
        msg1 = self.font_xl.render(self.message, True, color)
        msg2 = self.font_md.render("Prem R per reiniciar", True, C_TEXT)
        cx, cy = WIN_W//2, WIN_H//2
        self.screen.blit(msg1, msg1.get_rect(center=(cx, cy-20)))
        self.screen.blit(msg2, msg2.get_rect(center=(cx, cy+20)))

    # ── Event loop ───────────────────────────
    def run(self):
        KEY_DIRS = {
            pygame.K_UP:    (-1, 0), pygame.K_DOWN:  (1, 0),
            pygame.K_LEFT:  (0, -1), pygame.K_RIGHT: (0, 1),
            pygame.K_w:     (-1, 0), pygame.K_s:     (1, 0),
            pygame.K_a:     (0, -1), pygame.K_d:     (0, 1),
            # Diagonals via numpad
            pygame.K_KP7:   (-1,-1), pygame.K_KP8:  (-1, 0), pygame.K_KP9: (-1, 1),
            pygame.K_KP4:   (0, -1),                          pygame.K_KP6: (0,  1),
            pygame.K_KP1:   (1, -1), pygame.K_KP2:  (1,  0), pygame.K_KP3: (1,  1),
            # Q/E for diagonals
            pygame.K_q:     (-1,-1), pygame.K_e:    (-1, 1),
            pygame.K_z:     (1, -1), pygame.K_c:    (1,  1),
        }
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.new_game()
                    elif event.key in KEY_DIRS and not self.game_over:
                        self.move(*KEY_DIRS[event.key])

                if self.btn_hint.is_clicked(event):
                    self.toggle_hint()
                if self.btn_god.is_clicked(event):
                    self.toggle_god()
                if self.btn_reset.is_clicked(event):
                    self.new_game()

            self.draw()


if __name__ == "__main__":
    game = LaberintGame()
    game.run()
