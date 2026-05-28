# mystery_box.py
# The MysteryBox class. Spawns on the grid in Twisted mode.
# When the snake eats it, a two-stage randomizer picks an effect:
#   Stage 1 — 70% good pool, 30% bad pool
#   Stage 2 — random pick from whichever pool was chosen

import pygame
import random
from game.settings import CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, MYSTERY

# --- Effect pools ---
# Add new effect names here as we build them out.
# The randomizer uses len(pool) automatically, so just append to the list.
GOOD_EFFECTS = [
    "speed_boost",      # snake moves faster for POWERUP_DURATION seconds
    "golden_fruit",     # spawns a gold fruit on the grid worth 5 points
    # "double_points",  # coming soon
    # "bonus_spawn",    # coming soon
    # "magnet",         # coming soon
]

BAD_EFFECTS = [
    # "slow_down",      # coming soon
    # "shrink",         # coming soon
    # "split_decoy",    # coming soon
]


class MysteryBox:
    def __init__(self, grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT):
        # Store grid dimensions so spawn() picks a cell inside the right arena
        self.grid_width  = grid_width
        self.grid_height = grid_height
        self.position    = (0, 0)
        self.active      = False   # False = not on the grid yet

    def spawn(self, occupied):
        # Pick a random cell that isn't already taken by the snake, food, etc.
        while True:
            x = random.randint(0, self.grid_width  - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in occupied:
                self.position = (x, y)
                self.active   = True
                break

    def despawn(self):
        # Remove the box from the grid (called after the snake eats it)
        self.active = False

    def roll_effect(self):
        # Stage 1 — decide which pool to pull from
        if random.randint(1, 100) <= 70:
            pool = GOOD_EFFECTS
        else:
            pool = BAD_EFFECTS

        # Stage 2 — pick a random effect from that pool
        # If a pool is empty (not built yet), fall back to the other one
        if not pool:
            pool = GOOD_EFFECTS if pool is BAD_EFFECTS else BAD_EFFECTS

        return random.choice(pool)

    def draw(self, screen):
        # Only draw if the box is currently on the grid
        if not self.active:
            return

        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        # Fill with mystery color, then a bright white border to make it pop
        pygame.draw.rect(screen, MYSTERY, rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
