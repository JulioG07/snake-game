# game.py
# The Game class. This is the manager that runs everything.
# It owns the snake and food, runs the main loop, and draws the screen.

import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS,
    GRAY, WHITE, GREEN, GOLD, SNAKE_SPEED,
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER,
)
from game.snake import Snake, UP, DOWN, LEFT, RIGHT
from game.food import Food


class Game:
    def __init__(self):
        # Start pygame and create the window
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Three font sizes: small for HUD, mid for menu options, large for the title
        self.font       = pygame.font.SysFont("Arial", 24)
        self.font_large = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_mid   = pygame.font.SysFont("Arial", 32)

        # The game starts on the menu — player picks Classic or Twisted before anything is created
        self.mode  = None
        self.state = STATE_MENU

        # Snake and food don't exist yet — they're created in start_game() once a mode is picked
        self.snake = None
        self.food  = None
        self.score = 0
        self.move_timer = 0
        self.move_delay = 1.0 / SNAKE_SPEED  # seconds between snake steps

    def start_game(self, mode):
        # Called when the player picks a mode from the menu.
        # Creates fresh game objects and jumps into STATE_PLAYING.
        self.mode  = mode
        self.snake = Snake()
        self.food  = Food()
        self.food.respawn(self.snake.body)  # make sure food doesn't spawn on the snake
        self.score = 0
        self.state = STATE_PLAYING
        self.move_timer = 0
        self.move_delay = 1.0 / SNAKE_SPEED

    def handle_events(self):
        # Process every event pygame has queued up since the last frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # signals run() to exit the loop

            if event.type == pygame.KEYDOWN:

                if self.state == STATE_MENU:
                    # 1 = Classic, 2 = Twisted
                    if event.key == pygame.K_1:
                        self.start_game("classic")
                    elif event.key == pygame.K_2:
                        self.start_game("twisted")

                elif self.state == STATE_PLAYING:
                    # Arrow keys change the snake's queued direction
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(RIGHT)

                elif self.state == STATE_GAME_OVER:
                    # R takes the player back to the menu so they can pick a mode again
                    if event.key == pygame.K_r:
                        self.state = STATE_MENU

        return True

    def update(self, dt):
        # Only run game logic when actively playing
        if self.state != STATE_PLAYING:
            return

        # Accumulate time; move the snake once enough time has passed
        self.move_timer += dt

        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            self.snake.move()

            # Did the snake's head land on the food?
            if self.snake.get_head() == self.food.position:
                self.snake.grow()
                self.score += self.food.points
                self.food.respawn(self.snake.body)

            # Did the snake die (hit a wall or itself)?
            if self.snake.hit_wall() or self.snake.hit_self():
                self.state = STATE_GAME_OVER

    def draw(self):
        # Clear the screen each frame
        self.screen.fill(GRAY)

        if self.state == STATE_MENU:
            self._draw_menu()
        else:
            # Draw the food and snake on top of the background
            self.food.draw(self.screen)
            self.snake.draw(self.screen)

            # HUD: score in the top-left corner
            score_text = self.font.render("Score: " + str(self.score), True, WHITE)
            self.screen.blit(score_text, (10, 10))

            # Overlay the game-over message if the player has died
            if self.state == STATE_GAME_OVER:
                self._draw_game_over()

        # Push everything we drew to the actual display
        pygame.display.flip()

    def _draw_menu(self):
        # Title centered near the top
        title = self.font_large.render("Snake, but better.", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 140))

        # Two mode options — Classic in green, Twisted in gold
        classic_text = self.font_mid.render("1  --  Classic", True, GREEN)
        twisted_text = self.font_mid.render("2  --  Twisted", True, GOLD)
        self.screen.blit(classic_text, (SCREEN_WIDTH // 2 - classic_text.get_width() // 2, 300))
        self.screen.blit(twisted_text, (SCREEN_WIDTH // 2 - twisted_text.get_width() // 2, 360))

        # Small hint at the bottom so the player knows what to press
        hint = self.font.render("Press 1 or 2 to choose a mode", True, (150, 150, 150))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 460))

    def _draw_game_over(self):
        # "Game Over" centered in the middle of the screen
        over_text  = self.font_mid.render("Game Over", True, WHITE)
        retry_text = self.font.render("Press R to return to menu", True, (150, 150, 150))
        self.screen.blit(over_text,  (SCREEN_WIDTH // 2 - over_text.get_width()  // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def run(self):
        # The main game loop — keeps running until the window is closed
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # time since last frame in seconds
            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
