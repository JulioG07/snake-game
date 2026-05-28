# snake.py
# The Snake class.
# The snake's body is a list of (x, y) grid positions.
# The first item is the head, the last item is the tail.

import pygame
from game.settings import CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, GREEN, DARK_GREEN

# Directions as (x change, y change)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self, grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT):
        # Store the grid dimensions so hit_wall() knows where the edges are
        self.grid_width  = grid_width
        self.grid_height = grid_height

        # Start in the middle of the grid
        start_x = grid_width  // 2
        start_y = grid_height // 2

        # Build a body of 3 segments in a row (head first)
        self.body = []
        for i in range(3):
            self.body.append((start_x - i, start_y))

        # Start moving right
        self.direction      = RIGHT
        self.next_direction = RIGHT

        # Becomes True when the snake should grow on its next move
        self.grow_pending = False

    def get_head(self):
        # The head is the first item in the body list
        return self.body[0]

    def change_direction(self, new_direction):
        # Don't let the snake turn directly back on itself
        opposite_x = self.direction[0] * -1
        opposite_y = self.direction[1] * -1
        opposite = (opposite_x, opposite_y)

        if new_direction != opposite:
            self.next_direction = new_direction

    def move(self):
        # Apply the queued direction
        self.direction = self.next_direction

        # Work out where the new head goes
        head_x, head_y = self.get_head()
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Add the new head to the front
        self.body.insert(0, new_head)

        # If we are not growing, remove the tail
        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def grow(self):
        # The snake will grow by one on the next move
        self.grow_pending = True

    def shrink(self, amount):
        # Remove segments from the tail, but always keep the head
        for i in range(amount):
            if len(self.body) > 1:
                self.body.pop()

    def hit_self(self):
        # Check if the head touches any other body part
        head = self.get_head()
        for segment in self.body[1:]:
            if segment == head:
                return True
        return False

    def hit_wall(self):
        # Check if the head went off the grid — uses stored dimensions, not hardcoded constants
        head_x, head_y = self.get_head()
        if head_x < 0 or head_x >= self.grid_width:
            return True
        if head_y < 0 or head_y >= self.grid_height:
            return True
        return False

    def draw(self, screen):
        # Draw each segment as a square
        for i in range(len(self.body)):
            x, y = self.body[i]

            # Head is darker so you can tell them apart
            if i == 0:
                color = DARK_GREEN
            else:
                color = GREEN

            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
