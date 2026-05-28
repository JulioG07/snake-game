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
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, rect)


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
        # Only draw if currently on the grid
        if not self.active:
            return
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        # Gold fill with a bright yellow border to stand out from regular red food
        pygame.draw.rect(screen, GOLD, rect)
        pygame.draw.rect(screen, (255, 255, 0), rect, 2)
