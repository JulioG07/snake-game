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
        draw_snake_body(screen, self.body, self.direction, GREEN, DARK_GREEN)


def draw_snake_body(screen, cells, direction, body_color, head_color,
                    eye_white_r=4, eye_pupil_r=2, show_head=True):
    if not cells:
        return

    r = CELL_SIZE // 2 - 1

    # Pass 1 — connectors between adjacent segment centers
    for i in range(len(cells) - 1):
        x1, y1 = cells[i]
        x2, y2 = cells[i + 1]
        if abs(x2 - x1) + abs(y2 - y1) != 1:
            continue
        cx1 = x1 * CELL_SIZE + CELL_SIZE // 2
        cy1 = y1 * CELL_SIZE + CELL_SIZE // 2
        cx2 = x2 * CELL_SIZE + CELL_SIZE // 2
        cy2 = y2 * CELL_SIZE + CELL_SIZE // 2
        color = head_color if (i == 0 and show_head) else body_color
        if x1 == x2:
            pygame.draw.rect(screen, color, (cx1 - r, min(cy1, cy2), 2 * r, abs(cy2 - cy1)))
        else:
            pygame.draw.rect(screen, color, (min(cx1, cx2), cy1 - r, abs(cx2 - cx1), 2 * r))

    # Pass 2 — circles at each segment center (tail → head so head is on top)
    for i in range(len(cells) - 1, -1, -1):
        x, y = cells[i]
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, head_color if (i == 0 and show_head) else body_color, (cx, cy), r)

    # Pass 3 — eyes on the head (skipped when show_head is False)
    if not show_head:
        return

    hx, hy = cells[0]
    hcx = hx * CELL_SIZE + CELL_SIZE // 2
    hcy = hy * CELL_SIZE + CELL_SIZE // 2
    dx, dy = direction
    fwd  = CELL_SIZE // 4
    perp = CELL_SIZE // 4

    if   dx ==  1: eyes = [(hcx + fwd, hcy - perp), (hcx + fwd, hcy + perp)]
    elif dx == -1: eyes = [(hcx - fwd, hcy - perp), (hcx - fwd, hcy + perp)]
    elif dy == -1: eyes = [(hcx - perp, hcy - fwd), (hcx + perp, hcy - fwd)]
    else:          eyes = [(hcx - perp, hcy + fwd), (hcx + perp, hcy + fwd)]

    for ex, ey in eyes:
        pygame.draw.circle(screen, (255, 255, 255), (ex, ey), eye_white_r)
        pygame.draw.circle(screen, (0,   0,   0),   (ex, ey), eye_pupil_r)
