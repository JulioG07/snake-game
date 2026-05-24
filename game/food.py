# food.py
# The Food class. The snake eats it to grow and score points.
# Food sits on a random empty cell in the grid.

import pygame
import random
from game.settings import CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, RED, REGULAR_FOOD_POINTS


class Food:
    def __init__(self):
        self.points = REGULAR_FOOD_POINTS
        self.position = (0, 0)
        # Put it somewhere to start (snake gets passed in later spawns)
        self.respawn([])

    def respawn(self, snake_body):
        # Pick a random empty cell that the snake is not on
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            new_position = (x, y)

            # Make sure the food does not land on the snake
            if new_position not in snake_body:
                self.position = new_position
                break

    def draw(self, screen):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, rect)