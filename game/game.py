# game.py
# The Game class. This is the manager that runs everything.
# It owns the snake and food, runs the main loop, and draws the screen.

import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, CELL_SIZE,
    GRAY, WHITE, SNAKE_SPEED,
    STATE_PLAYING, STATE_GAME_OVER,
)
from game.snake import Snake, UP, DOWN, LEFT, RIGHT
from game.food import Food


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
        # Make a fresh snake and food, reset score and state
        self.snake = Snake()
        self.food = Food()
        self.food.respawn(self.snake.body)
        self.score = 0
        self.state = STATE_PLAYING

        # This timer controls how often the snake moves.
        self.move_timer = 0
        self.move_delay = 1.0 / SNAKE_SPEED

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.change_direction(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction(RIGHT)
                elif event.key == pygame.K_r and self.state == STATE_GAME_OVER:
                    self.reset()

        return True

    def update(self, dt):
        if self.state != STATE_PLAYING:
            return

        self.move_timer += dt

        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            self.snake.move()

            # Did the snake eat the food?
            if self.snake.get_head() == self.food.position:
                self.snake.grow()
                self.score += self.food.points
                self.food.respawn(self.snake.body)

            # Did the snake die?
            if self.snake.hit_wall() or self.snake.hit_self():
                self.state = STATE_GAME_OVER

    def draw(self):
        self.screen.fill(GRAY)

        self.food.draw(self.screen)
        self.snake.draw(self.screen)

        score_text = self.font.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(score_text, (10, 10))

        if self.state == STATE_GAME_OVER:
            over_text = self.font.render("Game Over - press R to restart", True, WHITE)
            x = SCREEN_WIDTH // 2 - over_text.get_width() // 2
            y = SCREEN_HEIGHT // 2
            self.screen.blit(over_text, (x, y))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()