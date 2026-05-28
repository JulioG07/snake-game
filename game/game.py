# game.py
# The Game class. This is the manager that runs everything.
# It owns the snake, food, and (in Twisted mode) the mystery box.
# Runs the main loop and draws the screen.

import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS,
    TWISTED_SCREEN_WIDTH, TWISTED_SCREEN_HEIGHT,
    TWISTED_GRID_WIDTH, TWISTED_GRID_HEIGHT,
    CELL_SIZE, GRID_WIDTH, GRID_HEIGHT,
    GRAY, WHITE, GREEN, GOLD, BLUE,
    SNAKE_SPEED, SPEED_BOOST_MULT, POWERUP_DURATION,
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER,
)
from game.snake import Snake, UP, DOWN, LEFT, RIGHT
from game.food import Food, GoldenFruit
from game.mystery_box import MysteryBox


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
        self.mode     = None
        self.state    = STATE_MENU
        self.screen_w = SCREEN_WIDTH   # updated in start_game() once a mode is chosen
        self.screen_h = SCREEN_HEIGHT

        # Game objects — created in start_game() once a mode is picked
        self.snake = None
        self.food  = None
        self.score = 0
        self.move_timer = 0
        self.move_delay = 1.0 / SNAKE_SPEED  # seconds between snake steps

        # Mystery box (Twisted mode only)
        self.mystery_box      = None
        self.box_spawn_timer  = 0     # counts up; box spawns when it hits BOX_SPAWN_RATE
        self.BOX_SPAWN_RATE   = 10.0  # seconds between mystery box spawns

        # Active effect tracking — only one effect runs at a time
        self.active_effect  = None   # name of the current effect, e.g. "speed_boost"
        self.effect_timer   = 0.0    # counts down to 0, then the effect ends

    def start_game(self, mode):
        # Called when the player picks a mode from the menu.
        # Creates fresh game objects and jumps into STATE_PLAYING.
        self.mode = mode

        # Pick arena dimensions based on mode, then resize the window
        if mode == "twisted":
            sw, sh = TWISTED_SCREEN_WIDTH, TWISTED_SCREEN_HEIGHT
            gw, gh = TWISTED_GRID_WIDTH,   TWISTED_GRID_HEIGHT
        else:
            sw, sh = SCREEN_WIDTH,  SCREEN_HEIGHT
            gw, gh = GRID_WIDTH,    GRID_HEIGHT

        # Resize the pygame window and store dimensions for use in draw methods
        self.screen   = pygame.display.set_mode((sw, sh))
        self.screen_w = sw
        self.screen_h = sh

        # Pass the grid dimensions into each object so they stay within the right arena
        self.snake = Snake(gw, gh)
        self.food  = Food(gw, gh)
        self.food.respawn(self.snake.body)
        self.score = 0
        self.state = STATE_PLAYING
        self.move_timer = 0
        self.move_delay = 1.0 / SNAKE_SPEED

        # Reset mystery box state for a fresh game
        self.mystery_box     = MysteryBox(gw, gh)
        self.box_spawn_timer = 0
        self.active_effect   = None
        self.effect_timer    = 0.0

        # Golden fruit — inactive until the mystery box gives it
        self.golden_fruit = GoldenFruit(gw, gh)

    def _apply_effect(self, effect):
        # Apply the given effect to the game and start its countdown timer.
        # Each new effect overwrites the previous one (only one active at a time).
        self.active_effect = effect
        self.effect_timer  = POWERUP_DURATION

        if effect == "speed_boost":
            # Make the snake step faster by shrinking the delay between moves
            self.move_delay = 1.0 / (SNAKE_SPEED * SPEED_BOOST_MULT)

        elif effect == "golden_fruit":
            # Spawn the golden fruit on an empty cell — no timed effect on the snake
            occupied = set(self.snake.body) | {self.food.position} | {self.mystery_box.position}
            self.golden_fruit.spawn(occupied)
            # Golden fruit has no timer so we don't need active_effect or effect_timer
            self.active_effect = None
            self.effect_timer  = 0.0

    def _end_effect(self):
        # Called when the effect timer runs out — revert everything back to normal.
        if self.active_effect == "speed_boost":
            self.move_delay = 1.0 / SNAKE_SPEED  # back to base speed

        self.active_effect = None
        self.effect_timer  = 0.0

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

        # --- Effect countdown ---
        # Tick down the active effect timer; end the effect when it expires
        if self.active_effect:
            self.effect_timer -= dt
            if self.effect_timer <= 0:
                self._end_effect()

        # --- Twisted mode: mystery box spawning ---
        if self.mode == "twisted":
            if not self.mystery_box.active:
                # Count up until it's time to spawn a new box
                self.box_spawn_timer += dt
                if self.box_spawn_timer >= self.BOX_SPAWN_RATE:
                    self.box_spawn_timer = 0
                    # Pass all occupied cells so the box doesn't overlap anything
                    occupied = set(self.snake.body) | {self.food.position}
                    self.mystery_box.spawn(occupied)

        # --- Snake movement (timer-based) ---
        # Accumulate time; move the snake once enough time has passed
        self.move_timer += dt

        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            self.snake.move()

            head = self.snake.get_head()

            # Did the snake's head land on the regular food?
            if head == self.food.position:
                self.snake.grow()
                self.score += self.food.points
                self.food.respawn(self.snake.body)

            # Did the snake's head land on the mystery box? (Twisted only)
            if self.mode == "twisted" and self.mystery_box.active:
                if head == self.mystery_box.position:
                    effect = self.mystery_box.roll_effect()  # two-stage randomizer
                    self._apply_effect(effect)
                    self.mystery_box.despawn()               # remove box from grid
                    self.box_spawn_timer = 0                 # reset spawn cooldown

            # Did the snake's head land on the golden fruit? (Twisted only)
            if self.mode == "twisted" and self.golden_fruit.active:
                if head == self.golden_fruit.position:
                    self.score += self.golden_fruit.points   # +5 points
                    self.golden_fruit.despawn()              # remove from grid

            # Did the snake die (hit a wall or itself)?
            if self.snake.hit_wall() or self.snake.hit_self():
                self.state = STATE_GAME_OVER

    def draw(self):
        # Clear the screen each frame
        self.screen.fill(GRAY)

        if self.state == STATE_MENU:
            self._draw_menu()
        else:
            # Draw food, mystery box (if active), and the snake
            self.food.draw(self.screen)

            if self.mode == "twisted":
                self.mystery_box.draw(self.screen)
                self.golden_fruit.draw(self.screen)   # only draws if active

            self.snake.draw(self.screen)

            # HUD: score in the top-left corner
            score_text = self.font.render("Score: " + str(self.score), True, WHITE)
            self.screen.blit(score_text, (10, 10))

            # HUD: show the active effect name and remaining time (Twisted only)
            if self.mode == "twisted" and self.active_effect:
                secs_left  = max(0, int(self.effect_timer) + 1)
                effect_text = self.font.render(
                    self.active_effect.replace("_", " ").upper() + "  " + str(secs_left) + "s",
                    True, BLUE
                )
                self.screen.blit(effect_text, (self.screen_w - effect_text.get_width() - 10, 10))

            # Overlay the game-over message if the player has died
            if self.state == STATE_GAME_OVER:
                self._draw_game_over()

        # Push everything we drew to the actual display
        pygame.display.flip()

    def _draw_menu(self):
        # Menu always uses the Classic window size (600x600) since no mode is active yet
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
        # "Game Over" centered in the middle of the current arena
        over_text  = self.font_mid.render("Game Over", True, WHITE)
        retry_text = self.font.render("Press R to return to menu", True, (150, 150, 150))
        self.screen.blit(over_text,  (self.screen_w // 2 - over_text.get_width()  // 2, self.screen_h // 2 - 30))
        self.screen.blit(retry_text, (self.screen_w // 2 - retry_text.get_width() // 2, self.screen_h // 2 + 20))

    def run(self):
        # The main game loop — keeps running until the window is closed
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # time since last frame in seconds
            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
