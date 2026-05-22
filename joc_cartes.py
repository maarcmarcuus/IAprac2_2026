"""
Joc de Cartes - El Senyor dels Anells
Part 2 of the 'El Senyor dels Anells' AI practice.

Two players (human vs machine) each have a deck of 10 cards:
  - 6 bronze, 3 silver, 1 gold
Hierarchy: must free all 6 bronze before silver, all 3 silver before gold.
Machine uses Minimax with Alpha-Beta pruning.
Winner: first player to free the gold ring card.
"""

import pygame
import sys
import random
import math
from copy import deepcopy

# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────
WIN_W = 1100
WIN_H = 700

FPS = 30

BRONZE = "bronze"
SILVER = "silver"
GOLD   = "gold"

CARD_W = 70
CARD_H = 100

# Weights for utility function
WEIGHTS = {BRONZE: 1, SILVER: 3, GOLD: 10}

# Minimax depth
MINIMAX_DEPTH = 4

# Colours
C_BG          = (20,  25,  35)
C_PANEL       = (28,  33,  48)
C_TEXT        = (220, 220, 220)
C_TEXT_DIM    = (130, 130, 150)
C_GOLD        = (230, 200,  10)
C_SILVER      = (180, 180, 190)
C_BRONZE      = (180, 100,  20)
C_CARD_BG     = (50,  55,  70)
C_CARD_BACK   = (40,  45,  60)
C_CARD_BORDER = (90,  90, 110)
C_SELECTED    = (80, 160, 255)
C_BTN         = (60,  80, 120)
C_BTN_H       = (80, 120, 180)
C_BTN_DIS     = (50,  50,  60)
C_WIN         = (30, 200,  30)
C_LOSE        = (200,  30,  30)
C_DIVIDER     = (60,  65,  80)
C_LOG_BG      = (15,  18,  28)
C_REVEALED_BG = (35,  45,  60)

RING_COLORS = {BRONZE: C_BRONZE, SILVER: C_SILVER, GOLD: C_GOLD}


# ─────────────────────────────────────────────
#  Card & deck helpers
# ─────────────────────────────────────────────
def make_deck():
    """Create a shuffled deck of 10 cards."""
    deck = [BRONZE]*6 + [SILVER]*3 + [GOLD]*1
    random.shuffle(deck)
    return deck


def can_free(card_type, freed):
    """Check if a card can be freed given the already-freed list."""
    bronze_count = freed.count(BRONZE)
    silver_count = freed.count(SILVER)
    if card_type == BRONZE:
        return True
    if card_type == SILVER:
        return bronze_count >= 6
    if card_type == GOLD:
        return bronze_count >= 6 and silver_count >= 3
    return False


def utility(human_freed, machine_freed):
    """Utility from machine's perspective: machine score - human score."""
    def score(freed):
        return sum(WEIGHTS[c] for c in freed)
    return score(machine_freed) - score(human_freed)


# ─────────────────────────────────────────────
#  Game State (immutable-ish for minimax)
# ─────────────────────────────────────────────
class GameState:
    __slots__ = [
        'human_freed', 'machine_freed',
        'human_reserved', 'machine_reserved',
        'human_deck', 'machine_deck',
        'human_revealed', 'machine_revealed',
        'turn',  # 'human' or 'machine'
        'human_blocked', 'machine_blocked',
        'game_over', 'winner'
    ]

    def __init__(self):
        self.human_freed    = []
        self.machine_freed  = []
        self.human_reserved  = None   # single reserved card or None
        self.machine_reserved = None
        self.human_deck     = make_deck()
        self.machine_deck   = make_deck()
        self.human_revealed  = None
        self.machine_revealed = None
        self.turn           = 'human'
        self.human_blocked  = False
        self.machine_blocked = False
        self.game_over      = False
        self.winner         = None

    def copy(self):
        s = GameState.__new__(GameState)
        s.human_freed     = self.human_freed[:]
        s.machine_freed   = self.machine_freed[:]
        s.human_reserved  = self.human_reserved
        s.machine_reserved = self.machine_reserved
        s.human_deck      = self.human_deck[:]
        s.machine_deck    = self.machine_deck[:]
        s.human_revealed  = self.human_revealed
        s.machine_revealed = self.machine_revealed
        s.turn            = self.turn
        s.human_blocked   = self.human_blocked
        s.machine_blocked = self.machine_blocked
        s.game_over       = self.game_over
        s.winner          = self.winner
        return s

    def reveal_for_turn(self):
        """Draw the top card for the current player if not already revealed."""
        if self.turn == 'human' and self.human_revealed is None:
            if self.human_deck:
                self.human_revealed = self.human_deck.pop(0)
        elif self.turn == 'machine' and self.machine_revealed is None:
            if self.machine_deck:
                self.machine_revealed = self.machine_deck.pop(0)

    def _check_win(self, player):
        if player == 'human':
            if GOLD in self.human_freed:
                self.game_over = True
                self.winner = 'human'
        else:
            if GOLD in self.machine_freed:
                self.game_over = True
                self.winner = 'machine'

    # ── Actions for the CURRENT player ──────
    def action_free_revealed(self):
        """Free the currently revealed card."""
        s = self.copy()
        card = s.human_revealed if s.turn == 'human' else s.machine_revealed
        if card is None:
            return None
        freed = s.human_freed if s.turn == 'human' else s.machine_freed
        if not can_free(card, freed):
            return None
        freed.append(card)
        if s.turn == 'human':
            s.human_revealed = None
        else:
            s.machine_revealed = None
        s._check_win(s.turn)
        if not s.game_over:
            s._end_turn()
        return s

    def action_reserve_revealed(self):
        """Reserve the currently revealed card (discard to reserve slot)."""
        s = self.copy()
        if s.turn == 'human':
            if s.human_revealed is None or s.human_reserved is not None:
                return None
            s.human_reserved = s.human_revealed
            s.human_revealed = None
        else:
            if s.machine_revealed is None or s.machine_reserved is not None:
                return None
            s.machine_reserved = s.machine_revealed
            s.machine_revealed = None
        s._end_turn()
        return s

    def action_free_reserved(self):
        """Free the reserved card (if hierarchy allows)."""
        s = self.copy()
        if s.turn == 'human':
            card = s.human_reserved
            freed = s.human_freed
        else:
            card = s.machine_reserved
            freed = s.machine_freed
        if card is None:
            return None
        if not can_free(card, freed):
            return None
        freed.append(card)
        if s.turn == 'human':
            s.human_reserved = None
        else:
            s.machine_reserved = None
        s._check_win(s.turn)
        if not s.game_over:
            s._end_turn()
        return s

    def action_return_to_deck(self):
        """Return revealed card to deck and shuffle."""
        s = self.copy()
        if s.turn == 'human':
            card = s.human_revealed
            if card is None:
                return None
            s.human_deck.append(card)
            random.shuffle(s.human_deck)
            s.human_revealed = None
        else:
            card = s.machine_revealed
            if card is None:
                return None
            s.machine_deck.append(card)
            random.shuffle(s.machine_deck)
            s.machine_revealed = None
        s._end_turn()
        return s

    def action_block_opponent(self):
        """Block the opponent's next turn."""
        s = self.copy()
        if s.turn == 'human':
            if s.human_revealed is None:
                return None
            # Discard revealed card to use this action
            s.human_deck.append(s.human_revealed)
            random.shuffle(s.human_deck)
            s.human_revealed = None
            s.machine_blocked = True
        else:
            if s.machine_revealed is None:
                return None
            s.machine_deck.append(s.machine_revealed)
            random.shuffle(s.machine_deck)
            s.machine_revealed = None
            s.human_blocked = True
        s._end_turn()
        return s

    def _end_turn(self):
        """Switch to next player, handling blocked turns."""
        if self.turn == 'human':
            self.turn = 'machine'
            if self.machine_blocked:
                self.machine_blocked = False
                self.turn = 'human'  # machine skips, back to human
        else:
            self.turn = 'human'
            if self.human_blocked:
                self.human_blocked = False
                self.turn = 'machine'  # human skips, back to machine

    def get_actions(self):
        """Return list of (action_name, resulting_state) for current player."""
        actions = []
        # Must first reveal a card if none revealed
        s = self.copy()
        s.reveal_for_turn()

        for name, method in [
            ('free_revealed',   s.action_free_revealed),
            ('reserve_revealed', s.action_reserve_revealed),
            ('free_reserved',   s.action_free_reserved),
            ('return_to_deck',  s.action_return_to_deck),
            ('block_opponent',  s.action_block_opponent),
        ]:
            result = method()
            if result is not None:
                actions.append((name, result))
        return actions


# ─────────────────────────────────────────────
#  Minimax with Alpha-Beta
# ─────────────────────────────────────────────
def minimax(state, depth, alpha, beta, maximizing):
    """
    Minimax with alpha-beta pruning.
    maximizing=True when it's machine's turn.
    Returns (utility_value, best_action_name).
    """
    if state.game_over:
        if state.winner == 'machine':
            return 10000, None
        elif state.winner == 'human':
            return -10000, None
        return 0, None

    if depth == 0:
        return utility(state.human_freed, state.machine_freed), None

    actions = state.get_actions()
    if not actions:
        return utility(state.human_freed, state.machine_freed), None

    best_action = None

    if maximizing:
        best_val = -math.inf
        for name, next_state in actions:
            val, _ = minimax(next_state, depth - 1, alpha, beta, next_state.turn == 'machine')
            if val > best_val:
                best_val = val
                best_action = name
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break
        return best_val, best_action
    else:
        best_val = math.inf
        for name, next_state in actions:
            val, _ = minimax(next_state, depth - 1, alpha, beta, next_state.turn == 'machine')
            if val < best_val:
                best_val = val
                best_action = name
            beta = min(beta, best_val)
            if beta <= alpha:
                break
        return best_val, best_action


def machine_choose_action(state):
    """Run minimax and return the best action name."""
    # Make sure card is revealed
    s = state.copy()
    s.reveal_for_turn()
    _, best_action = minimax(s, MINIMAX_DEPTH, -math.inf, math.inf, True)
    if best_action is None and s.get_actions():
        best_action = s.get_actions()[0][0]
    return best_action


# ─────────────────────────────────────────────
#  Button
# ─────────────────────────────────────────────
class Button:
    def __init__(self, rect, label):
        self.rect  = pygame.Rect(rect)
        self.label = label
        self.enabled = True

    def draw(self, surf, font):
        color = C_BTN if self.enabled else C_BTN_DIS
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        pygame.draw.rect(surf, C_CARD_BORDER, self.rect, 1, border_radius=6)
        tc = C_TEXT if self.enabled else C_TEXT_DIM
        txt = font.render(self.label, True, tc)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (self.enabled and
                event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ─────────────────────────────────────────────
#  Drawing helpers
# ─────────────────────────────────────────────
def draw_card(surf, x, y, card_type, small=False):
    """Draw a single card face-up."""
    w = CARD_W if not small else 44
    h = CARD_H if not small else 62
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surf, C_CARD_BG, rect, border_radius=6)
    pygame.draw.rect(surf, C_CARD_BORDER, rect, 2, border_radius=6)
    color = RING_COLORS[card_type]
    cx, cy = x + w//2, y + h//2
    r = w//2 - 8
    pygame.draw.circle(surf, color, (cx, cy), r)
    pygame.draw.circle(surf, C_CARD_BG, (cx, cy), r - 10 if not small else r - 6)
    # Label
    font_size = 11 if not small else 9
    font = pygame.font.SysFont("monospace", font_size, bold=True)
    label = {"bronze": "BR", "silver": "PL", "gold": "OR"}[card_type]
    txt = font.render(label, True, color)
    surf.blit(txt, txt.get_rect(center=(cx, cy + r + 8 if not small else cy + r + 5)))


def draw_card_back(surf, x, y, small=False):
    """Draw a card face-down."""
    w = CARD_W if not small else 44
    h = CARD_H if not small else 62
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surf, C_CARD_BACK, rect, border_radius=6)
    pygame.draw.rect(surf, C_CARD_BORDER, rect, 2, border_radius=6)
    # Pattern
    for i in range(3, w-3, 8):
        for j in range(3, h-3, 8):
            pygame.draw.rect(surf, (55, 60, 75), (x+i, y+j, 4, 4), border_radius=1)


# ─────────────────────────────────────────────
#  Main game class
# ─────────────────────────────────────────────
class JocCartesGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Joc de Cartes - El Senyor dels Anells")
        self.clock = pygame.time.Clock()

        self.font_sm  = pygame.font.SysFont("monospace", 13)
        self.font_md  = pygame.font.SysFont("monospace", 15, bold=True)
        self.font_lg  = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_xl  = pygame.font.SysFont("monospace", 26, bold=True)

        self.log = []           # list of strings for game log
        self.machine_thinking = False
        self.machine_timer = 0  # ms to wait before machine acts (for visual delay)
        self.MACHINE_DELAY = 900

        self._init_buttons()
        self.new_game()

    def _init_buttons(self):
        bw, bh = 170, 36
        # Human action buttons (placed in center area)
        bx = WIN_W//2 - bw//2
        self.btn_free_revealed  = Button((bx, 310, bw, bh), "Alliberar revelada")
        self.btn_reserve        = Button((bx, 355, bw, bh), "Reservar revelada")
        self.btn_free_reserved  = Button((bx, 400, bw, bh), "Alliberar reservada")
        self.btn_return_deck    = Button((bx, 445, bw, bh), "Tornar al munt")
        self.btn_block_opp      = Button((bx, 490, bw, bh), "Bloquejar maquina")
        self.btn_new_game       = Button((WIN_W//2 - 80, WIN_H - 50, 160, 36), "NOU JOC")
        self.human_buttons = [
            self.btn_free_revealed, self.btn_reserve,
            self.btn_free_reserved, self.btn_return_deck,
            self.btn_block_opp
        ]

    def new_game(self):
        self.state = GameState()
        self.log = ["=== NOU JOC ==="]
        self.machine_thinking = False
        self.machine_timer = 0
        self._update_button_states()

    def _update_button_states(self):
        s = self.state
        is_human_turn = (s.turn == 'human') and not s.game_over

        for btn in self.human_buttons:
            btn.enabled = is_human_turn

        if is_human_turn:
            # Reveal check
            revealed = s.human_revealed
            # free_revealed: need a revealed card and it must be freeable
            self.btn_free_revealed.enabled = (
                revealed is not None and
                can_free(revealed, s.human_freed)
            )
            # reserve: need revealed card and no current reservation
            self.btn_reserve.enabled = (
                revealed is not None and
                s.human_reserved is None
            )
            # free reserved: need reserved card and it must be freeable
            self.btn_free_reserved.enabled = (
                s.human_reserved is not None and
                can_free(s.human_reserved, s.human_freed)
            )
            # return to deck: need revealed card
            self.btn_return_deck.enabled = revealed is not None
            # block opponent: need revealed card
            self.btn_block_opp.enabled = revealed is not None

    def _add_log(self, msg):
        self.log.append(msg)
        if len(self.log) > 40:
            self.log = self.log[-40:]

    def _human_reveal_if_needed(self):
        """Reveal human's card if it's their turn and no card is shown."""
        if self.state.turn == 'human' and self.state.human_revealed is None:
            if self.state.human_deck:
                self.state.human_revealed = self.state.human_deck.pop(0)
                self._add_log(f"Reveles: {self.state.human_revealed.upper()}")
            else:
                self._add_log("Munt buit! No pots revelar.")
            self._update_button_states()

    def _apply_human_action(self, action_name):
        if self.state.game_over:
            return
        # Ensure card is revealed
        if self.state.human_revealed is None:
            self._human_reveal_if_needed()
            if self.state.human_revealed is None:
                return

        method_map = {
            'free_revealed':    self.state.action_free_revealed,
            'reserve_revealed': self.state.action_reserve_revealed,
            'free_reserved':    self.state.action_free_reserved,
            'return_to_deck':   self.state.action_return_to_deck,
            'block_opponent':   self.state.action_block_opponent,
        }
        method = method_map.get(action_name)
        if method is None:
            return
        new_state = method()
        if new_state is None:
            self._add_log("Accio no valida!")
            return

        self.state = new_state

        # Logging
        log_msgs = {
            'free_revealed':    "Alliberes la carta revelada.",
            'reserve_revealed': "Reserves la carta revelada.",
            'free_reserved':    "Alliberes la carta reservada.",
            'return_to_deck':   "Tornes la carta al munt.",
            'block_opponent':   "Bloqueges el torn de la maquina!",
        }
        self._add_log(f"Tu: {log_msgs[action_name]}")

        if self.state.game_over:
            if self.state.winner == 'human':
                self._add_log("HAS GUANYAT!")
            else:
                self._add_log("LA MAQUINA GUANYA!")
            return

        # If now machine's turn, schedule machine move
        if self.state.turn == 'machine':
            self.machine_thinking = True
            self.machine_timer = pygame.time.get_ticks() + self.MACHINE_DELAY

        self._update_button_states()

    def _machine_take_turn(self):
        """Execute the machine's turn."""
        if self.state.turn != 'machine' or self.state.game_over:
            self.machine_thinking = False
            return

        # Reveal machine card
        if self.state.machine_revealed is None:
            if self.state.machine_deck:
                self.state.machine_revealed = self.state.machine_deck.pop(0)
                self._add_log(f"Maquina revela: {self.state.machine_revealed.upper()}")
            else:
                self._add_log("Maquina: munt buit!")
                self.state._end_turn()
                self.machine_thinking = False
                self._update_button_states()
                return

        best_action = machine_choose_action(self.state)
        if best_action is None:
            self._add_log("Maquina: no pot actuar, passa torn.")
            self.state._end_turn()
            self.machine_thinking = False
            self._update_button_states()
            return

        method_map = {
            'free_revealed':    self.state.action_free_revealed,
            'reserve_revealed': self.state.action_reserve_revealed,
            'free_reserved':    self.state.action_free_reserved,
            'return_to_deck':   self.state.action_return_to_deck,
            'block_opponent':   self.state.action_block_opponent,
        }
        method = method_map.get(best_action)
        if method:
            new_state = method()
            if new_state:
                self.state = new_state

        log_msgs = {
            'free_revealed':    "Maquina allibera carta revelada.",
            'reserve_revealed': "Maquina reserva carta revelada.",
            'free_reserved':    "Maquina allibera carta reservada.",
            'return_to_deck':   "Maquina torna carta al munt.",
            'block_opponent':   "Maquina BLOQUEJA el teu torn!",
        }
        self._add_log(log_msgs.get(best_action, f"Maquina: {best_action}"))

        if self.state.game_over:
            if self.state.winner == 'machine':
                self._add_log("LA MAQUINA GUANYA!")
            else:
                self._add_log("HAS GUANYAT!")

        self.machine_thinking = False
        self._update_button_states()

        # If still machine's turn (blocked human), schedule another machine move
        if not self.state.game_over and self.state.turn == 'machine':
            self.machine_thinking = True
            self.machine_timer = pygame.time.get_ticks() + self.MACHINE_DELAY

    # ── Drawing ──────────────────────────────────────────────
    def draw(self):
        self.screen.fill(C_BG)
        s = self.state

        self._draw_dividers()
        self._draw_machine_area(s)
        self._draw_human_area(s)
        self._draw_center_area(s)
        self._draw_log()
        self._draw_turn_indicator(s)

        if s.game_over:
            self._draw_game_over(s)

        pygame.display.flip()

    def _draw_dividers(self):
        # Horizontal dividers
        pygame.draw.line(self.screen, C_DIVIDER, (0, 240), (WIN_W - 250, 240), 2)
        pygame.draw.line(self.screen, C_DIVIDER, (0, 530), (WIN_W - 250, 530), 2)
        # Vertical: log panel
        pygame.draw.line(self.screen, C_DIVIDER, (WIN_W - 250, 0), (WIN_W - 250, WIN_H), 2)

    def _draw_machine_area(self, s):
        # Title
        title = self.font_lg.render("MAQUINA", True, (200, 80, 80))
        self.screen.blit(title, (20, 10))

        if s.machine_blocked:
            blocked = self.font_md.render("[TORN BLOQUEJAT]", True, (255, 80, 80))
            self.screen.blit(blocked, (160, 14))

        x = 20
        y = 40

        # Freed cards
        freed_lbl = self.font_sm.render("Alliberades:", True, C_TEXT_DIM)
        self.screen.blit(freed_lbl, (x, y))
        cx = x + 110
        for card in s.machine_freed:
            draw_card(self.screen, cx, y - 5, card, small=True)
            cx += 50
        y += 70

        # Reserved
        res_lbl = self.font_sm.render("Reservada:", True, C_TEXT_DIM)
        self.screen.blit(res_lbl, (x, y))
        if s.machine_reserved:
            draw_card(self.screen, x + 100, y - 5, s.machine_reserved, small=True)
        else:
            pygame.draw.rect(self.screen, C_CARD_BACK, (x + 100, y - 5, 44, 62), 1, border_radius=4)
        y += 70

        # Deck info
        deck_lbl = self.font_sm.render(f"Munt: {len(s.machine_deck)} cartes", True, C_TEXT_DIM)
        self.screen.blit(deck_lbl, (x, y))
        if s.machine_deck:
            draw_card_back(self.screen, x + 150, y - 10, small=True)

        # Revealed card
        rev_x = 500
        rev_y = 80
        rev_lbl = self.font_sm.render("Revelada:", True, C_TEXT_DIM)
        self.screen.blit(rev_lbl, (rev_x, 45))
        if s.machine_revealed:
            draw_card(self.screen, rev_x, rev_y, s.machine_revealed)
        else:
            pygame.draw.rect(self.screen, C_CARD_BACK, (rev_x, rev_y, CARD_W, CARD_H), 1, border_radius=6)

        # Thinking indicator
        if self.machine_thinking:
            think = self.font_md.render("Pensant...", True, (200, 200, 50))
            self.screen.blit(think, (rev_x + CARD_W + 20, rev_y + 35))

        # Score
        machine_score = sum(WEIGHTS[c] for c in s.machine_freed)
        sc_lbl = self.font_md.render(f"Punts: {machine_score}", True, (200, 80, 80))
        self.screen.blit(sc_lbl, (700, 10))

    def _draw_human_area(self, s):
        y_base = 540
        x = 20

        title = self.font_lg.render("TU (JUGADOR)", True, (80, 180, 80))
        self.screen.blit(title, (x, y_base))

        if s.human_blocked:
            blocked = self.font_md.render("[TORN BLOQUEJAT]", True, (255, 80, 80))
            self.screen.blit(blocked, (200, y_base + 4))

        y = y_base + 30

        # Freed cards
        freed_lbl = self.font_sm.render("Alliberades:", True, C_TEXT_DIM)
        self.screen.blit(freed_lbl, (x, y))
        cx = x + 110
        for card in s.human_freed:
            draw_card(self.screen, cx, y - 5, card, small=True)
            cx += 50
        y += 70

        # Reserved
        res_lbl = self.font_sm.render("Reservada:", True, C_TEXT_DIM)
        self.screen.blit(res_lbl, (x, y))
        if s.human_reserved:
            draw_card(self.screen, x + 100, y - 5, s.human_reserved, small=True)
        else:
            pygame.draw.rect(self.screen, C_CARD_BACK, (x + 100, y - 5, 44, 62), 1, border_radius=4)

        # Deck info
        deck_lbl = self.font_sm.render(f"Munt: {len(s.human_deck)} cartes", True, C_TEXT_DIM)
        self.screen.blit(deck_lbl, (x + 200, y))
        if s.human_deck:
            draw_card_back(self.screen, x + 350, y - 10, small=True)

        # Score
        human_score = sum(WEIGHTS[c] for c in s.human_freed)
        sc_lbl = self.font_md.render(f"Punts: {human_score}", True, (80, 180, 80))
        self.screen.blit(sc_lbl, (700, y_base))

        # Revealed card
        rev_x = 500
        rev_y = 560
        rev_lbl = self.font_sm.render("Revelada:", True, C_TEXT_DIM)
        self.screen.blit(rev_lbl, (rev_x, 540))
        if s.human_revealed:
            draw_card(self.screen, rev_x, rev_y, s.human_revealed)
        else:
            pygame.draw.rect(self.screen, C_CARD_BACK, (rev_x, rev_y, CARD_W, CARD_H), 1, border_radius=6)

    def _draw_center_area(self, s):
        # Action buttons (center)
        if not s.game_over:
            for btn in self.human_buttons:
                btn.draw(self.screen, self.font_md)

        # Hierarchy guide
        guide_x = WIN_W - 250 - 300
        guide_y = 260
        guide_lbl = self.font_sm.render("Jerarquia: Bronze(6) -> Plata(3) -> Or(1)", True, C_TEXT_DIM)
        self.screen.blit(guide_lbl, (20, guide_y))

        # Turn label
        turn_x = WIN_W//2 - 120
        turn_y = 255
        if not s.game_over:
            turn_who = "EL TEU TORN" if s.turn == 'human' else "TORN MAQUINA"
            turn_col = (80, 200, 80) if s.turn == 'human' else (200, 80, 80)
            turn_surf = self.font_lg.render(turn_who, True, turn_col)
            self.screen.blit(turn_surf, (turn_x, turn_y))

        # Reveal button (available when human turn and no card revealed)
        if s.turn == 'human' and s.human_revealed is None and not s.game_over:
            reveal_surf = self.font_md.render("[ Revela carta -> fes una accio ]", True, (200, 200, 80))
            self.screen.blit(reveal_surf, (WIN_W//2 - 170, 285))

        # New game button
        self.btn_new_game.draw(self.screen, self.font_md)

    def _draw_log(self):
        log_x = WIN_W - 248
        pygame.draw.rect(self.screen, C_LOG_BG, (log_x, 0, 248, WIN_H))
        log_title = self.font_md.render("REGISTRE", True, C_GOLD)
        self.screen.blit(log_title, (log_x + 10, 10))
        y = 35
        for line in self.log[-30:]:
            if len(line) > 28:
                line = line[:28]
            color = C_TEXT
            if "GUANYA" in line or "NOU JOC" in line:
                color = C_GOLD
            elif "Maquina" in line or "MAQUINA" in line:
                color = (200, 100, 100)
            elif "Tu:" in line or "Reveles" in line:
                color = (100, 200, 100)
            elif "BLOQUEJ" in line:
                color = (255, 140, 0)
            surf = self.font_sm.render(line, True, color)
            self.screen.blit(surf, (log_x + 8, y))
            y += 17
            if y > WIN_H - 20:
                break

    def _draw_turn_indicator(self, s):
        # Highlight the active player area
        if not s.game_over:
            if s.turn == 'human':
                pygame.draw.rect(self.screen, (40, 80, 40), (0, 530, WIN_W - 250, 4))
            else:
                pygame.draw.rect(self.screen, (80, 30, 30), (0, 236, WIN_W - 250, 4))

    def _draw_game_over(self, s):
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        if s.winner == 'human':
            msg = "HAS GUANYAT!"
            color = C_WIN
        else:
            msg = "LA MAQUINA GUANYA!"
            color = C_LOSE

        cx, cy = WIN_W//2, WIN_H//2
        msg_surf = self.font_xl.render(msg, True, color)
        self.screen.blit(msg_surf, msg_surf.get_rect(center=(cx, cy - 30)))

        sub = self.font_md.render("Prem 'NOU JOC' per tornar a jugar", True, C_TEXT)
        self.screen.blit(sub, sub.get_rect(center=(cx, cy + 20)))

        # Show final scores
        hs = sum(WEIGHTS[c] for c in s.human_freed)
        ms = sum(WEIGHTS[c] for c in s.machine_freed)
        score_txt = self.font_md.render(f"Tu: {hs} pts  |  Maquina: {ms} pts", True, C_TEXT_DIM)
        self.screen.blit(score_txt, score_txt.get_rect(center=(cx, cy + 55)))

        self.btn_new_game.draw(self.screen, self.font_md)

    # ── Event loop ───────────────────────────────────────────
    def run(self):
        while True:
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()

            # Machine turn trigger
            if self.machine_thinking and now >= self.machine_timer:
                self._machine_take_turn()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.new_game()

                if self.btn_new_game.is_clicked(event):
                    self.new_game()

                if not self.machine_thinking and not self.state.game_over:
                    # Reveal human card automatically when it's their turn
                    if self.state.turn == 'human' and self.state.human_revealed is None:
                        if any(btn.is_clicked(event) for btn in self.human_buttons):
                            self._human_reveal_if_needed()

                    if self.btn_free_revealed.is_clicked(event):
                        self._apply_human_action('free_revealed')
                    elif self.btn_reserve.is_clicked(event):
                        self._apply_human_action('reserve_revealed')
                    elif self.btn_free_reserved.is_clicked(event):
                        self._apply_human_action('free_reserved')
                    elif self.btn_return_deck.is_clicked(event):
                        self._apply_human_action('return_to_deck')
                    elif self.btn_block_opp.is_clicked(event):
                        self._apply_human_action('block_opponent')

            # Auto-reveal for human if their turn and no card
            if (not self.state.game_over and
                    self.state.turn == 'human' and
                    self.state.human_revealed is None and
                    not self.machine_thinking and
                    self.state.human_deck):
                self._human_reveal_if_needed()

            # Auto-trigger machine turn
            if (not self.state.game_over and
                    self.state.turn == 'machine' and
                    not self.machine_thinking):
                self.machine_thinking = True
                self.machine_timer = pygame.time.get_ticks() + self.MACHINE_DELAY

            self.draw()


if __name__ == "__main__":
    game = JocCartesGame()
    game.run()
