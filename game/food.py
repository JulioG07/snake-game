# food.py
# Food classes — regular food and golden fruit.
# Both sit on a random empty cell until the snake eats them.

import pygame
import random
from game.settings import (
    CELL_SIZE, GRID_WIDTH, GRID_HEIGHT,
    RED, GOLD,
    REGULAR_FOOD_POINTS, BONUS_FOOD_POINTS,
)


class Food:
    def __init__(self, grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT):
        # Store grid dimensions so respawn() uses the right boundaries for this mode
        self.grid_width  = grid_width
        self.grid_height = grid_height
        self.points      = REGULAR_FOOD_POINTS
        self.position    = (0, 0)
        # Put it somewhere to start (snake gets passed in later spawns)
        self.respawn([])

    def respawn(self, snake_body):
        # Pick a random empty cell that the snake is not on
        while True:
            x = random.randint(0, self.grid_width  - 1)
            y = random.randint(0, self.grid_height - 1)
            new_position = (x, y)

            # Make sure the food does not land on the snake
            if new_position not in snake_body:
                self.position = new_position
                break

    def draw(self, screen):
        x, y = self.position
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2

        # Two cherries side by side
        r = 8
        lc = (cx - 6, cy + 6)   # left cherry center
        rc = (cx + 6, cy + 6)   # right cherry center

        # Stems drawn first so cherry circles cover the base of each stem
        # Each stem curves up and inward in two segments, meeting at a junction,
        # then a short main branch goes straight up from there
        junction = (cx, cy - 10)
        pygame.draw.line(screen, (30, 130, 30), (cx - 6, cy - 2), (cx - 4, cy - 7), 2)
        pygame.draw.line(screen, (30, 130, 30), (cx - 4, cy - 7), junction, 2)
        pygame.draw.line(screen, (30, 130, 30), (cx + 6, cy - 2), (cx + 4, cy - 7), 2)
        pygame.draw.line(screen, (30, 130, 30), (cx + 4, cy - 7), junction, 2)
        pygame.draw.line(screen, (30, 130, 30), junction, (cx, cy - 13), 2)

        pygame.draw.circle(screen, (200, 30, 30), lc, r)
        pygame.draw.circle(screen, (200, 30, 30), rc, r)
        pygame.draw.circle(screen, (140, 10, 10), lc, r, 1)
        pygame.draw.circle(screen, (140, 10, 10), rc, r, 1)
        pygame.draw.circle(screen, (255, 100, 100), (lc[0] - 2, lc[1] - 2), 2)
        pygame.draw.circle(screen, (255, 100, 100), (rc[0] - 2, rc[1] - 2), 2)


class GoldenFruit:
    def __init__(self, grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT):
        # Store grid dimensions so spawn() stays within the right arena
        self.grid_width  = grid_width
        self.grid_height = grid_height
        self.points      = BONUS_FOOD_POINTS  # worth 5 points
        self.position    = (0, 0)
        self.active      = False  # only exists on the grid after the mystery box gives it

    def spawn(self, occupied):
        # Pick a random empty cell not already taken by the snake, food, or box
        while True:
            x = random.randint(0, self.grid_width  - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in occupied:
                self.position = (x, y)
                self.active   = True
                break

    def despawn(self):
        # Remove from the grid when eaten
        self.active = False

    def draw(self, screen):
        if not self.active:
            return
        x, y = self.position
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2 + 2   # shift down slightly for stem room

        # Apple body
        pygame.draw.circle(screen, (255, 200, 0), (cx, cy), 11)
        pygame.draw.circle(screen, (200, 150, 0), (cx, cy), 11, 1)
        # Highlight
        pygame.draw.circle(screen, (255, 240, 120), (cx - 3, cy - 3), 3)
        # Stem
        stem_base = (cx + 1, cy - 11)
        stem_top  = (cx + 1, cy - 15)
        pygame.draw.line(screen, (100, 60, 10), stem_base, stem_top, 2)
        # Leaf
        leaf_points = [(cx + 1, cy - 13), (cx + 7, cy - 16), (cx + 4, cy - 11)]
        pygame.draw.polygon(screen, (30, 160, 30), leaf_points)
