# The Game class. This is the manager that runs everything.
# It owns the snake, runs the main loop, and draws the screen.

import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, CELL_SIZE,
    GRAY, WHITE, SNAKE_SPEED,
    STATE_PLAYING, STATE_GAME_OVER,
)
from game.snake import Snake, UP, DOWN, LEFT, RIGHT


class Game:
    def __init__(self):
        # Start pygame and make the window
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Font for the score text
        self.font = pygame.font.SysFont("Arial", 24)

        # Set up the starting game pieces
        self.reset()

    def reset(self):
        # Make a fresh snake and reset score and state
        self.snake = Snake()
        self.score = 0
        self.state = STATE_PLAYING

        # This timer controls how often the snake moves.
        # The snake moves SNAKE_SPEED times per second.
        self.move_timer = 0
        self.move_delay = 1.0 / SNAKE_SPEED

    def handle_events(self):
        # Look at everything the player did this frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                # Arrow keys change the snake's direction
                if event.key == pygame.K_UP:
                    self.snake.change_direction(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction(RIGHT)

                # R restarts after game over
                elif event.key == pygame.K_r and self.state == STATE_GAME_OVER:
                    self.reset()

        return True

    def update(self, dt):
        # Only move the snake while playing
        if self.state != STATE_PLAYING:
            return

        # Add the time since the last frame to our timer
        self.move_timer += dt

        # When enough time has passed, move the snake one cell
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            self.snake.move()

            # Check if the snake died
            if self.snake.hit_wall() or self.snake.hit_self():
                self.state = STATE_GAME_OVER

    def draw(self):
        # Clear the screen
        self.screen.fill(GRAY)

        # Draw the snake
        self.snake.draw(self.screen)

        # Draw the score in the top left
        score_text = self.font.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # If the game is over, show a message
        if self.state == STATE_GAME_OVER:
            over_text = self.font.render("Game Over - press R to restart", True, WHITE)
            x = SCREEN_WIDTH // 2 - over_text.get_width() // 2
            y = SCREEN_HEIGHT // 2
            self.screen.blit(over_text, (x, y))

        # Show everything we just drew
        pygame.display.flip()

    def run(self):
        # The main game loop
        running = True
        while running:
            # dt = time since last frame, in seconds
            dt = self.clock.tick(FPS) / 1000.0

            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()