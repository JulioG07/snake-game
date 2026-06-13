# game.py
# The Game class. This is the manager that runs everything.
# It owns the snake, food, and (in Twisted mode) the mystery box.
# Runs the main loop and draws the screen.

import json
import math
import os
import pygame
import random
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS,
    TWISTED_SCREEN_WIDTH, TWISTED_SCREEN_HEIGHT,
    TWISTED_GRID_WIDTH, TWISTED_GRID_HEIGHT,
    CELL_SIZE, GRID_WIDTH, GRID_HEIGHT,
    GRAY, WHITE, GREEN, DARK_GREEN, GOLD, BLUE, ORANGE, DECOY, PORTAL_COLOR, WHITE_GRAY,
    CLASSIC_CELL_A, CLASSIC_CELL_B, TWISTED_CELL_A, TWISTED_CELL_B,
    SNAKE_SPEED, SPEED_BOOST_MULT, POWERUP_DURATION, SPEED_BOOST_DURATION, MAGNET_DURATION, DECOY_DURATION, PORTAL_DURATION, MAGNET_RANGE,
    EVENT_COOLDOWN, OBSTACLE_CHUNK_INTERVAL, OBSTACLE_MAX_CHUNKS, OBSTACLE_ACTIVE_TIME, OBSTACLE_MIN_CELLS, OBSTACLE_MAX_CELLS,
    ANACONDA_LENGTH, ANACONDA_SPEED, ANACONDA_BODY, ANACONDA_HEAD_C,
    HORDE_MIN_COUNT, HORDE_MAX_COUNT, HORDE_SNAKE_MIN_LEN, HORDE_SNAKE_MAX_LEN,
    HORDE_SPEED, HORDE_WARNING_TIME, HORDE_VULNERABLE, BABY_SNAKE, BABY_SNAKE_HEAD, VULNERABLE,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER,
    HIGH_SCORE_FILE,
)
from game.snake import Snake, UP, DOWN, LEFT, RIGHT, draw_snake_body
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
        self.BOX_SPAWN_RATE   = 8.0   # seconds between mystery box spawns

        # Active effect tracking — only one effect runs at a time
        self.active_effect  = None   # name of the current effect, e.g. "speed_boost"
        self.effect_timer   = 0.0    # counts down to 0, then the effect ends

        self.high_score = self._load_high_score()

        self.death_flash_timer  = 0.0
        self.fade_alpha         = 0
        self.fade_pending_mode  = None
        self.fade_delay         = 0.0

        # Sounds
        _root = os.path.dirname(os.path.dirname(__file__))
        def _snd(path):
            try:
                return pygame.mixer.Sound(os.path.join(_root, path))
            except FileNotFoundError:
                return None
        self.snd_startgame = _snd("assets/sounds/ui/startgame.mp3")
        self.snd_eating    = _snd("assets/sounds/gameplay/eating.wav")
        self.snd_score     = _snd("assets/sounds/gameplay/score.wav")
        self.snd_death     = _snd("assets/sounds/gameplay/death.mp3")
        if self.snd_death: self.snd_death.set_volume(0.15)
        self.snd_pause     = _snd("assets/sounds/ui/pause.mp3")
        self.snd_spawn        = _snd("assets/sounds/events/spawn.wav")
        self.snd_anaconda     = _snd("assets/sounds/events/anaconda.wav")
        self.snd_horde        = _snd("assets/sounds/events/horde.wav")
        self.snd_powerup      = _snd("assets/sounds/powerups/powerup_sound.mp3")
        self.snd_open_portal  = _snd("assets/sounds/powerups/open_portal.mp3")
        self.snd_close_portal = _snd("assets/sounds/powerups/close_portal.mp3")
        self.snd_cut          = _snd("assets/sounds/powerups/cut.wav")
        # self.snd_move         = _snd("assets/sounds/gameplay/move.mp3")

        # Background snake for the menu screen
        self.menu_snake_cells = []
        self.menu_snake_dir   = (1, 0)
        self.menu_snake_timer = 0.0
        self.menu_snake_speed = 0.10  # seconds per step
        self._init_menu_snake()

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
        self.score             = 0
        self.state             = STATE_PLAYING
        self.new_record_played = False
        self.move_timer = 0
        self.move_delay = 1.0 / SNAKE_SPEED

        # Reset mystery box state for a fresh game
        self.mystery_box     = MysteryBox(gw, gh)
        self.box_spawn_timer = 0
        self.active_effect   = None
        self.effect_timer    = 0.0

        # Golden fruit — inactive until the mystery box gives it
        self.golden_fruit = GoldenFruit(gw, gh)

        # Bonus foods — list of (x, y) positions that spawn when bonus_spawn rolls
        # Each item is eaten individually and removed from the list
        self.bonus_foods = []

        # Split decoy — stationary segments left behind after the tail breaks off
        self.decoy_segments = []
        self.decoy_timer    = 0.0

        # Portals — two linked teleport tiles; empty list when inactive
        self.portals          = []
        self.portal_timer     = 0.0
        self.portal_cooldown  = 0   # steps remaining before portals can fire again

        # Random event system
        self.active_event      = None
        self.event_cooldown    = EVENT_COOLDOWN
        self.event_phase       = None   # "spawning", "active", or "despawning"
        self.event_phase_timer = 0.0
        self.chunk_timer       = 0.0
        self.obstacle_chunks   = []
        self.chunks_spawned    = 0

        # Anaconda event
        self.anaconda_cells          = []
        self.anaconda_head           = (0, 0)
        self.anaconda_dir            = (0, 0)
        self.anaconda_timer          = 0.0
        self.anaconda_warning_timer  = 0.0

        # Horde event — list of dicts: {'cells', 'ghost_head', 'max_len'}
        self.horde_snakes        = []
        self.horde_dir           = (0, 0)
        self.horde_timer         = 0.0
        self.horde_warning_timer = 0.0   # counts down warning phase
        self.death_flash_timer   = 0.0

    def _load_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f).get('high_score', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def _save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)

    def _all_occupied(self):
        occupied = set(self.snake.body) | {self.food.position}
        if self.mystery_box.active:
            occupied.add(self.mystery_box.position)
        if self.golden_fruit.active:
            occupied.add(self.golden_fruit.position)
        occupied.update(self.bonus_foods)
        occupied.update(self.decoy_segments)
        occupied.update(self.portals)
        for chunk in self.obstacle_chunks:
            occupied.update(chunk)
        occupied.update(self.anaconda_cells)
        for s in self.horde_snakes:
            occupied.update(s['cells'])
        return occupied

    def _gen_obstacle_chunk(self, occupied):
        size = random.randint(OBSTACLE_MIN_CELLS, OBSTACLE_MAX_CELLS)
        # Find a valid anchor cell away from the very edge so chunks feel mid-grid
        for _ in range(200):
            ax = random.randint(1, self.snake.grid_width  - 2)
            ay = random.randint(1, self.snake.grid_height - 2)
            if (ax, ay) not in occupied:
                break
        else:
            return []  # grid too crowded, skip this chunk

        cells = [(ax, ay)]
        local_occ = set(occupied) | {(ax, ay)}
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for _ in range(size - 1):
            candidates = list(cells)
            random.shuffle(candidates)
            placed = False
            for cx, cy in candidates:
                shuffled_dirs = dirs[:]
                random.shuffle(shuffled_dirs)
                for dx, dy in shuffled_dirs:
                    nx, ny = cx + dx, cy + dy
                    if (0 <= nx < self.snake.grid_width and
                            0 <= ny < self.snake.grid_height and
                            (nx, ny) not in local_occ):
                        cells.append((nx, ny))
                        local_occ.add((nx, ny))
                        placed = True
                        break
                if placed:
                    break

        return cells

    def _start_random_event(self):
        choice = random.choice(["obstacle_wave", "anaconda", "horde"])
        if choice == "obstacle_wave":
            self.active_event    = "obstacle_wave"
            self.event_phase     = "spawning"
            self.chunk_timer     = OBSTACLE_CHUNK_INTERVAL
            self.chunks_spawned  = 0
            self.obstacle_chunks = []
        elif choice == "horde":
            self.active_event        = "horde"
            self.horde_warning_timer = HORDE_WARNING_TIME
            if self.snd_horde: self.snd_horde.play()
            self.horde_timer         = 0.0
            self.horde_snakes        = []
            horizontal = random.choice([True, False])
            if horizontal:
                self.horde_dir = (1, 0) if random.choice([True, False]) else (-1, 0)
                dx = self.horde_dir[0]
                count = random.randint(HORDE_MIN_COUNT, HORDE_MAX_COUNT)
                section = self.snake.grid_height // count
                for i in range(count):
                    row     = random.randint(i * section, (i + 1) * section - 1)
                    max_len = random.randint(HORDE_SNAKE_MIN_LEN, HORDE_SNAKE_MAX_LEN)
                    stagger = random.randint(0, 5) * (i + 1)
                    gx = (-1 - stagger) if dx == 1 else (self.snake.grid_width + stagger)
                    self.horde_snakes.append({'cells': [], 'ghost_head': (gx, row), 'max_len': max_len})
            else:
                self.horde_dir = (0, 1) if random.choice([True, False]) else (0, -1)
                dy = self.horde_dir[1]
                count = random.randint(HORDE_MIN_COUNT, HORDE_MAX_COUNT)
                section = self.snake.grid_width // count
                for i in range(count):
                    col     = random.randint(i * section, (i + 1) * section - 1)
                    max_len = random.randint(HORDE_SNAKE_MIN_LEN, HORDE_SNAKE_MAX_LEN)
                    stagger = random.randint(0, 5) * (i + 1)
                    gy = (-1 - stagger) if dy == 1 else (self.snake.grid_height + stagger)
                    self.horde_snakes.append({'cells': [], 'ghost_head': (col, gy), 'max_len': max_len})

        else:
            self.active_event          = "anaconda"
            self.anaconda_cells        = []
            self.anaconda_timer        = ANACONDA_SPEED
            self.anaconda_warning_timer = 2.0
            if self.snd_anaconda: self.snd_anaconda.play()
            if random.choice([True, False]):  # horizontal
                row = random.randint(0, self.snake.grid_height - 1)
                if random.choice([True, False]):  # left → right
                    self.anaconda_dir  = (1, 0)
                    self.anaconda_head = (-1, row)
                else:                            # right → left
                    self.anaconda_dir  = (-1, 0)
                    self.anaconda_head = (self.snake.grid_width, row)
            else:                              # vertical
                col = random.randint(0, self.snake.grid_width - 1)
                if random.choice([True, False]):  # top → bottom
                    self.anaconda_dir  = (0, 1)
                    self.anaconda_head = (col, -1)
                else:                            # bottom → top
                    self.anaconda_dir  = (0, -1)
                    self.anaconda_head = (col, self.snake.grid_height)

    def _check_anaconda_collision(self):
        anaconda_set = set(self.anaconda_cells)
        if not anaconda_set:
            return
        for pos in self.snake.body:
            if pos in anaconda_set:
                self.state             = STATE_GAME_OVER
                self.death_flash_timer = 0.4
                self.snd_death.play()
                self._save_high_score()
                return

    def _check_horde_collision(self):
        all_horde_cells = {c for s in self.horde_snakes for c in s['cells']}
        if not all_horde_cells:
            return
        vuln_len = min(HORDE_VULNERABLE, len(self.snake.body))
        for i, pos in enumerate(self.snake.body):
            if pos in all_horde_cells:
                if i < vuln_len or len(self.snake.body) <= HORDE_VULNERABLE:
                    self.state             = STATE_GAME_OVER
                    self.death_flash_timer = 0.4
                    self.snd_death.play()
                else:
                    severed = list(self.snake.body[i:])
                    self.snake.body = self.snake.body[:i]
                    self.decoy_segments.extend(severed)
                    self.decoy_timer = DECOY_DURATION
                    if self.snd_cut: self.snd_cut.play()
                return

    def _update_active_event(self, dt):
        if self.active_event == "obstacle_wave":
            self.chunk_timer += dt

            if self.event_phase == "spawning":
                if self.chunk_timer >= OBSTACLE_CHUNK_INTERVAL:
                    self.chunk_timer = 0.0
                    chunk = self._gen_obstacle_chunk(self._all_occupied())
                    if chunk:
                        self.obstacle_chunks.append(chunk)
                        if self.snd_spawn: self.snd_spawn.play()
                    self.chunks_spawned += 1
                    if self.chunks_spawned >= OBSTACLE_MAX_CHUNKS:
                        self.event_phase       = "active"
                        self.event_phase_timer = OBSTACLE_ACTIVE_TIME
                        self.chunk_timer       = 0.0

            elif self.event_phase == "active":
                self.event_phase_timer -= dt
                if self.event_phase_timer <= 0:
                    self.event_phase = "despawning"
                    self.chunk_timer = 0.0

            elif self.event_phase == "despawning":
                if self.chunk_timer >= OBSTACLE_CHUNK_INTERVAL:
                    self.chunk_timer = 0.0
                    if self.obstacle_chunks:
                        self.obstacle_chunks.pop(0)
                    if not self.obstacle_chunks:
                        self.active_event    = None
                        self.event_phase     = None
                        self.chunks_spawned  = 0
                        self.event_cooldown  = EVENT_COOLDOWN

        elif self.active_event == "anaconda":
            if self.anaconda_warning_timer > 0:
                self.anaconda_warning_timer -= dt
                return
            self.anaconda_timer += dt
            if self.anaconda_timer >= ANACONDA_SPEED:
                self.anaconda_timer = 0.0
                dx, dy = self.anaconda_dir
                hx, hy = self.anaconda_head
                self.anaconda_head = (hx + dx, hy + dy)
                hx, hy = self.anaconda_head

                # Sliding window: visible cells are the on-grid portion of the
                # ANACONDA_LENGTH body behind the ghost head. A 50-cell body on
                # a 26-cell grid covers the full row while the tail is still
                # off-screen on the entry side, so length > grid_width actually
                # matters and the head can exit while many body cells remain.
                self.anaconda_cells = []
                for i in range(ANACONDA_LENGTH):
                    bx = hx - dx * i
                    by = hy - dy * i
                    if 0 <= bx < self.snake.grid_width and 0 <= by < self.snake.grid_height:
                        self.anaconda_cells.append((bx, by))

                self._check_anaconda_collision()

                # Event ends when the tail cell has also exited the far side
                tx = hx - dx * (ANACONDA_LENGTH - 1)
                ty = hy - dy * (ANACONDA_LENGTH - 1)
                tail_exited = (
                    (dx ==  1 and tx >= self.snake.grid_width)  or
                    (dx == -1 and tx < 0)                       or
                    (dy ==  1 and ty >= self.snake.grid_height)  or
                    (dy == -1 and ty < 0)
                )
                if tail_exited:
                    self.active_event   = None
                    self.anaconda_cells = []
                    self.event_cooldown = EVENT_COOLDOWN

        elif self.active_event == "horde":
            if self.horde_warning_timer > 0:
                self.horde_warning_timer -= dt
                return  # wait out the warning phase before snakes move

            self.horde_timer += dt
            if self.horde_timer >= HORDE_SPEED:
                self.horde_timer = 0.0
                dx, dy = self.horde_dir
                for s in self.horde_snakes:
                    hx, hy = s['ghost_head']
                    s['ghost_head'] = (hx + dx, hy + dy)
                    hx, hy = s['ghost_head']
                    if 0 <= hx < self.snake.grid_width and 0 <= hy < self.snake.grid_height:
                        s['cells'].insert(0, (hx, hy))
                    head_off = (
                        (dx ==  1 and hx >= self.snake.grid_width)  or
                        (dx == -1 and hx < 0)                       or
                        (dy ==  1 and hy >= self.snake.grid_height)  or
                        (dy == -1 and hy < 0)
                    )
                    if len(s['cells']) > s['max_len'] or head_off:
                        if s['cells']:
                            s['cells'].pop()

                self._check_horde_collision()

                # Event ends when all snakes have fully exited
                if all(not s['cells'] for s in self.horde_snakes):
                    gw, gh = self.snake.grid_width, self.snake.grid_height
                    all_exited = all(
                        (dx ==  1 and s['ghost_head'][0] >= gw)  or
                        (dx == -1 and s['ghost_head'][0] < 0)    or
                        (dy ==  1 and s['ghost_head'][1] >= gh)  or
                        (dy == -1 and s['ghost_head'][1] < 0)
                        for s in self.horde_snakes
                    )
                    if all_exited:
                        self.active_event  = None
                        self.horde_snakes  = []
                        self.event_cooldown = EVENT_COOLDOWN

    def _magnet_pull(self, food_pos, head):
        fx, fy = food_pos
        hx, hy = head
        dx, dy = hx - fx, hy - fy
        if abs(dx) + abs(dy) > MAGNET_RANGE:
            return food_pos  # out of range, don't move
        # Step one cell along the axis with the larger gap
        if abs(dx) >= abs(dy):
            nx, ny = fx + (1 if dx > 0 else -1 if dx < 0 else 0), fy
        else:
            nx, ny = fx, fy + (1 if dy > 0 else -1 if dy < 0 else 0)
        # Stay on the grid
        if 0 <= nx < self.snake.grid_width and 0 <= ny < self.snake.grid_height:
            return (nx, ny)
        return food_pos

    def _apply_effect(self, effect):
        if self.active_effect:
            self._end_effect()

        if effect == "portal":
            if self.snd_open_portal: self.snd_open_portal.play()
        elif effect != "split_decoy":
            if self.snd_powerup: self.snd_powerup.play()

        self.active_effect = effect
        self.effect_timer  = POWERUP_DURATION

        if effect == "speed_boost":
            self.effect_timer = SPEED_BOOST_DURATION
            self.move_delay = 1.0 / (SNAKE_SPEED * SPEED_BOOST_MULT)

        elif effect == "magnet":
            self.effect_timer = MAGNET_DURATION

        elif effect == "golden_fruit":
            # Spawn the golden fruit on an empty cell — no timed effect on the snake
            occupied = set(self.snake.body) | {self.food.position} | {self.mystery_box.position}
            self.golden_fruit.spawn(occupied)
            # Golden fruit has no timer so we don't need active_effect or effect_timer
            self.active_effect = None
            self.effect_timer  = 0.0

        elif effect == "bonus_spawn":
            # Spawn 2-3 extra food items on random empty cells
            occupied = set(self.snake.body) | {self.food.position} | {self.mystery_box.position}
            count = random.randint(2, 3)
            for _ in range(count):
                while True:
                    x = random.randint(0, self.snake.grid_width  - 1)
                    y = random.randint(0, self.snake.grid_height - 1)
                    pos = (x, y)
                    # Make sure it doesn't overlap anything already on the grid
                    if pos not in occupied:
                        self.bonus_foods.append(pos)
                        occupied.add(pos)  # so the next item doesn't land on this one
                        break
            # No timed effect on the snake
            self.active_effect = None
            self.effect_timer  = 0.0

        elif effect == "portal":
            # Spawn two portals at random grid positions — fully random, could be near borders
            occupied = set(self.snake.body) | {self.food.position} | {self.mystery_box.position}
            self.portals = []
            for _ in range(2):
                while True:
                    x = random.randint(0, self.snake.grid_width  - 1)
                    y = random.randint(0, self.snake.grid_height - 1)
                    pos = (x, y)
                    if pos not in occupied:
                        self.portals.append(pos)
                        occupied.add(pos)
                        break
            self.portal_timer    = PORTAL_DURATION
            self.portal_cooldown = 0
            self.active_effect   = None
            self.effect_timer    = 0.0

        elif effect == "split_decoy":
            # 30-50% of the tail breaks off and becomes a stationary obstacle
            amount = max(1, int(len(self.snake.body) * random.uniform(0.30, 0.50)))
            amount = min(amount, len(self.snake.body) - 1)  # always keep the head
            self.decoy_segments.extend(self.snake.body[-amount:])
            self.snake.shrink(amount)
            self.decoy_timer   = DECOY_DURATION
            if self.snd_cut: self.snd_cut.play()
            self.active_effect = None
            self.effect_timer  = 0.0

    def _check_score_sound(self, prev_score):
        crossed_ten    = (self.score // 10) > (prev_score // 10)
        new_record     = self.score > self.high_score and not self.new_record_played
        if crossed_ten or new_record:
            self.snd_score.play()
        if new_record:
            self.new_record_played = True

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
                    if event.key == pygame.K_1 and not self.fade_pending_mode:
                        self.snd_startgame.play()
                        self.fade_pending_mode = "classic"
                        self.fade_delay        = 0.3
                    elif event.key == pygame.K_2 and not self.fade_pending_mode:
                        self.snd_startgame.play()
                        self.fade_pending_mode = "twisted"
                        self.fade_delay        = 0.3

                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.state = STATE_PAUSED
                        if self.snd_pause: self.snd_pause.play()

                    # Arrow keys change the snake's queued direction
                    elif event.key == pygame.K_UP:
                        self.snake.change_direction(UP)
                        # if self.snd_move: self.snd_move.play()
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(DOWN)
                        # if self.snd_move: self.snd_move.play()
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(LEFT)
                        # if self.snd_move: self.snd_move.play()
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(RIGHT)
                        # if self.snd_move: self.snd_move.play()

                elif self.state == STATE_PAUSED:
                    if event.key == pygame.K_SPACE:
                        self.state = STATE_PLAYING

                elif self.state == STATE_GAME_OVER:
                    # R takes the player back to the menu so they can pick a mode again
                    if event.key == pygame.K_r:
                        self.state    = STATE_MENU
                        self.screen_w = SCREEN_WIDTH
                        self.screen_h = SCREEN_HEIGHT
                        # Resize window back to the standard menu size
                        self.screen   = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        return True

    def _init_menu_snake(self):
        # Rows/cols that are clear of the title, buttons, and hint text
        safe_h_rows = [0, 1, 2, 3, 7, 13, 14, 16, 17, 18, 19]   # horizontal
        safe_v_cols = [0, 1, 2, 3, 16, 17, 18, 19]               # vertical (avoids centered UI)
        length = random.randint(5, 8)
        if random.choice([True, False]):   # horizontal
            row = random.choice(safe_h_rows)
            if random.choice([True, False]):
                self.menu_snake_dir   = (1, 0)
                self.menu_snake_cells = [(-1 - i, row) for i in range(length)]
            else:
                self.menu_snake_dir   = (-1, 0)
                self.menu_snake_cells = [(GRID_WIDTH + i, row) for i in range(length)]
        else:                              # vertical
            col = random.choice(safe_v_cols)
            if random.choice([True, False]):
                self.menu_snake_dir   = (0, 1)
                self.menu_snake_cells = [(col, -1 - i) for i in range(length)]
            else:
                self.menu_snake_dir   = (0, -1)
                self.menu_snake_cells = [(col, GRID_HEIGHT + i) for i in range(length)]

    def _update_menu_snake(self, dt):
        self.menu_snake_timer += dt
        if self.menu_snake_timer >= self.menu_snake_speed:
            self.menu_snake_timer = 0.0
            dx, dy = self.menu_snake_dir
            hx, hy = self.menu_snake_cells[0]
            self.menu_snake_cells.insert(0, (hx + dx, hy + dy))
            self.menu_snake_cells.pop()
            tx, ty = self.menu_snake_cells[-1]
            tail_gone = (
                (dx ==  1 and tx >= GRID_WIDTH)  or
                (dx == -1 and tx < 0)            or
                (dy ==  1 and ty >= GRID_HEIGHT) or
                (dy == -1 and ty < 0)
            )
            if tail_gone:
                self._init_menu_snake()

    def update(self, dt):
        if self.state == STATE_MENU:
            self._update_menu_snake(dt)
            if self.fade_pending_mode:
                if self.fade_delay > 0:
                    self.fade_delay -= dt
                else:
                    self.fade_alpha = min(255, self.fade_alpha + int(510 * dt))
                    if self.fade_alpha >= 255:
                        mode = self.fade_pending_mode
                        self.fade_pending_mode = None
                        self.fade_alpha        = 0
                        self.fade_delay        = 0.0
                        self.start_game(mode)
            return
        if self.state == STATE_PAUSED:
            return
        if self.state == STATE_GAME_OVER:
            if self.death_flash_timer > 0:
                self.death_flash_timer = max(0.0, self.death_flash_timer - dt)
            return
        if self.state != STATE_PLAYING:
            return

        # --- Effect countdown ---
        # Tick down the active effect timer; end the effect when it expires
        if self.active_effect:
            self.effect_timer -= dt
            if self.effect_timer <= 0:
                self._end_effect()

        # --- Portal timer ---
        if self.portals:
            self.portal_timer -= dt
            if self.portal_timer <= 0:
                self.portals      = []
                self.portal_timer = 0.0
                if self.snd_close_portal: self.snd_close_portal.play()

        # --- Decoy segment timer ---
        if self.decoy_segments:
            self.decoy_timer -= dt
            if self.decoy_timer <= 0:
                self.decoy_segments = []
                self.decoy_timer    = 0.0

        # --- Random event system (Twisted only) ---
        if self.mode == "twisted":
            if self.active_event is None:
                self.event_cooldown -= dt
                if self.event_cooldown <= 0:
                    self._start_random_event()
            else:
                self._update_active_event(dt)

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

            # Portal teleport — runs first so the correct head pos flows into all checks below
            if self.mode == "twisted" and self.portals:
                if self.portal_cooldown > 0:
                    self.portal_cooldown -= 1
                elif head == self.portals[0]:
                    self.snake.body[0] = self.portals[1]
                    head = self.portals[1]
                    self.portal_cooldown = 2
                elif head == self.portals[1]:
                    self.snake.body[0] = self.portals[0]
                    head = self.portals[0]
                    self.portal_cooldown = 2

            # Magnet: pull nearby food one step toward the head before collision checks
            if self.active_effect == "magnet":
                self.food.position = self._magnet_pull(self.food.position, head)
                if self.golden_fruit.active:
                    self.golden_fruit.position = self._magnet_pull(self.golden_fruit.position, head)
                for i, pos in enumerate(self.bonus_foods):
                    self.bonus_foods[i] = self._magnet_pull(pos, head)

            # Did the snake's head land on the regular food?
            if head == self.food.position:
                self.snake.grow()
                prev = self.score
                self.score += self.food.points
                self.snd_eating.play()
                self._check_score_sound(prev)
                self.food.respawn(self.snake.body)

            # Did the snake's head land on the mystery box? (Twisted only)
            if self.mode == "twisted" and self.mystery_box.active:
                if head == self.mystery_box.position:
                    effect = self.mystery_box.roll_effect()
                    self._apply_effect(effect)
                    self.mystery_box.despawn()
                    self.box_spawn_timer = 0

            # Did the snake's head land on the golden fruit? (Twisted only)
            if self.mode == "twisted" and self.golden_fruit.active:
                if head == self.golden_fruit.position:
                    prev = self.score
                    self.score += self.golden_fruit.points
                    self.snd_eating.play()
                    self._check_score_sound(prev)
                    self.golden_fruit.despawn()

            # Did the snake's head land on a bonus food item? (Twisted only)
            if self.mode == "twisted" and head in self.bonus_foods:
                self.bonus_foods.remove(head)
                prev = self.score
                self.score += 1
                self.snd_eating.play()
                self._check_score_sound(prev)

            # Horde collision — also checked here in case snake walks into a stationary horde cell
            if self.mode == "twisted" and self.horde_snakes:
                self._check_horde_collision()

            # Did the snake die (hit a wall, itself, a decoy, obstacle chunk, or anaconda)?
            hit_decoy    = self.mode == "twisted" and head in self.decoy_segments
            obstacle_cells = {c for chunk in self.obstacle_chunks for c in chunk}
            hit_obstacle = self.mode == "twisted" and head in obstacle_cells
            hit_anaconda = self.mode == "twisted" and head in self.anaconda_cells
            if self.snake.hit_wall() or self.snake.hit_self() or hit_decoy or hit_obstacle or hit_anaconda:
                self.state             = STATE_GAME_OVER
                self.death_flash_timer = 0.4
                self.snd_death.play()
                self._save_high_score()

    def draw(self):
        if self.state == STATE_MENU:
            self.screen.fill(GRAY)
            self._draw_menu()
        else:
            self._draw_grid()
            # Draw food, mystery box (if active), and the snake
            self.food.draw(self.screen)

            if self.mode == "twisted":
                self.mystery_box.draw(self.screen)
                self.golden_fruit.draw(self.screen)   # only draws if active

                # Draw each bonus food as an orange fruit
                for pos in self.bonus_foods:
                    x, y = pos
                    cx = x * CELL_SIZE + CELL_SIZE // 2
                    cy = y * CELL_SIZE + CELL_SIZE // 2
                    # Orange body
                    pygame.draw.circle(self.screen, (255, 140, 0), (cx, cy), 11)
                    pygame.draw.circle(self.screen, (210, 100, 0), (cx, cy), 11, 1)
                    # Highlight
                    pygame.draw.circle(self.screen, (255, 200, 80), (cx - 3, cy - 3), 3)
                    # Stem
                    pygame.draw.line(self.screen, (80, 50, 10),
                                     (cx, cy - 11), (cx, cy - 14), 2)
                    # Small leaf
                    pygame.draw.polygon(self.screen, (30, 150, 30),
                                        [(cx, cy - 13), (cx + 6, cy - 15), (cx + 3, cy - 11)])

                # Draw horde baby snakes
                for s in self.horde_snakes:
                    if s['cells']:
                        ghx, ghy = s['ghost_head']
                        head_on_grid = (
                            0 <= ghx < self.snake.grid_width and
                            0 <= ghy < self.snake.grid_height
                        )
                        draw_snake_body(self.screen, s['cells'], self.horde_dir,
                                        BABY_SNAKE, BABY_SNAKE_HEAD,
                                        eye_white_r=3, eye_pupil_r=1,
                                        show_head=head_on_grid)

                # Draw anaconda — hide head decoration once ghost head exits grid
                if self.anaconda_cells:
                    ahx, ahy = self.anaconda_head
                    anaconda_head_visible = (
                        0 <= ahx < self.snake.grid_width and
                        0 <= ahy < self.snake.grid_height
                    )
                    draw_snake_body(self.screen, self.anaconda_cells, self.anaconda_dir,
                                    ANACONDA_BODY, ANACONDA_HEAD_C,
                                    show_head=anaconda_head_visible)

                # Draw obstacle chunks as void tiles
                t_void = pygame.time.get_ticks() / 1000.0
                glow_alpha = int(60 + 40 * math.sin(t_void * 2))
                glow_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                glow_surf.fill((0, 0, 0, 0))
                pygame.draw.rect(glow_surf, (120, 40, 200, glow_alpha),
                                 (0, 0, CELL_SIZE, CELL_SIZE), 3)
                for chunk in self.obstacle_chunks:
                    for x, y in chunk:
                        rx = x * CELL_SIZE
                        ry = y * CELL_SIZE
                        pygame.draw.rect(self.screen, (10, 5, 18),
                                         (rx, ry, CELL_SIZE, CELL_SIZE))
                        self.screen.blit(glow_surf, (rx, ry))

                # Draw split decoy segments as snake-shaped circles (no head/eyes)
                if self.decoy_segments:
                    draw_snake_body(self.screen, self.decoy_segments, (1, 0),
                                    DECOY, DECOY, show_head=False)

                # Draw portals as pulsing ring + inner circle
                if self.portals:
                    t = pygame.time.get_ticks() / 1000.0
                    inner_r = max(2, int(CELL_SIZE * 0.18 + CELL_SIZE * 0.10 * math.sin(t * 5)))
                    outer_r = CELL_SIZE // 2 - 1
                    for pos in self.portals:
                        cx = pos[0] * CELL_SIZE + CELL_SIZE // 2
                        cy = pos[1] * CELL_SIZE + CELL_SIZE // 2
                        pygame.draw.circle(self.screen, PORTAL_COLOR, (cx, cy), outer_r, 3)
                        pygame.draw.circle(self.screen, PORTAL_COLOR, (cx, cy), inner_r)

            self.snake.draw(self.screen)

            # Magnet animation: pulsing ring around in-range food, drawn after snake so it's visible
            if self.mode == "twisted" and self.active_effect == "magnet":
                t = pygame.time.get_ticks() / 1000.0
                radius = int(CELL_SIZE // 2 + 4 + 3 * math.sin(t * 6))
                head = self.snake.get_head()
                candidates = [self.food.position]
                if self.golden_fruit.active:
                    candidates.append(self.golden_fruit.position)
                candidates.extend(self.bonus_foods)
                for pos in candidates:
                    if abs(pos[0] - head[0]) + abs(pos[1] - head[1]) <= MAGNET_RANGE:
                        cx = pos[0] * CELL_SIZE + CELL_SIZE // 2
                        cy = pos[1] * CELL_SIZE + CELL_SIZE // 2
                        pygame.draw.circle(self.screen, (0, 220, 220), (cx, cy), radius, 2)

            # Vulnerable segment glow during horde event — pulsing gold circle outline
            if self.mode == "twisted" and self.active_event == "horde":
                t = pygame.time.get_ticks() / 1000.0
                border_w = max(1, int(2 + 1 * math.sin(t * 3)))
                seg_r    = CELL_SIZE // 2 - 1
                vuln_len = min(HORDE_VULNERABLE, len(self.snake.body))
                for pos in self.snake.body[:vuln_len]:
                    cx = pos[0] * CELL_SIZE + CELL_SIZE // 2
                    cy = pos[1] * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, VULNERABLE, (cx, cy), seg_r, border_w)

            # HUD: score top-left, best score below it
            score_text = self.font.render("Score: " + str(self.score), True, WHITE)
            best_text  = self.font.render("Best:  " + str(self.high_score), True, GOLD)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(best_text,  (10, 36))

            # HUD: show the active effect name and remaining time (Twisted only)
            if self.mode == "twisted" and self.active_effect:
                secs_left  = max(0, int(self.effect_timer) + 1)
                effect_text = self.font.render(
                    self.active_effect.replace("_", " ").upper() + "  " + str(secs_left) + "s",
                    True, BLUE
                )
                self.screen.blit(effect_text, (self.screen_w - effect_text.get_width() - 10, 10))

            # Overlay the game-over or pause message if needed
            if self.state == STATE_GAME_OVER:
                self._draw_game_over()
            elif self.state == STATE_PAUSED:
                self._draw_pause()

        # Push everything we drew to the actual display
        pygame.display.flip()

    def _draw_grid(self):
        gw = self.snake.grid_width
        gh = self.snake.grid_height
        if self.mode == "twisted":
            ca, cb = TWISTED_CELL_A, TWISTED_CELL_B
        else:
            ca, cb = CLASSIC_CELL_A, CLASSIC_CELL_B

        for row in range(gh):
            for col in range(gw):
                color = ca if (col + row) % 2 == 0 else cb
                pygame.draw.rect(self.screen, color,
                                 (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Vignette: semi-transparent dark overlay around the arena edges (twisted only)
        if self.mode == "twisted":
            vignette_surf = pygame.Surface((gw * CELL_SIZE, gh * CELL_SIZE), pygame.SRCALPHA)
            depth = 80   # max alpha at the very edge
            steps = 5    # how many cells inward the fade reaches
            for i in range(steps):
                alpha = int(depth * (1 - i / steps))
                thick = CELL_SIZE
                # top / bottom / left / right bands
                pygame.draw.rect(vignette_surf, (0, 0, 0, alpha),
                                 (i * thick, i * thick,
                                  (gw - 2 * i) * thick, thick))
                pygame.draw.rect(vignette_surf, (0, 0, 0, alpha),
                                 (i * thick, (gh - i - 1) * thick,
                                  (gw - 2 * i) * thick, thick))
                pygame.draw.rect(vignette_surf, (0, 0, 0, alpha),
                                 (i * thick, i * thick,
                                  thick, (gh - 2 * i) * thick))
                pygame.draw.rect(vignette_surf, (0, 0, 0, alpha),
                                 ((gw - i - 1) * thick, i * thick,
                                  thick, (gh - 2 * i) * thick))
            self.screen.blit(vignette_surf, (0, 0))

    def _draw_pause(self):
        cx = self.screen_w // 2
        cy = self.screen_h // 2

        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        pw, ph = 280, 140
        px, py = cx - pw // 2, cy - ph // 2
        pygame.draw.rect(self.screen, (18, 18, 18), (px, py, pw, ph))
        pygame.draw.rect(self.screen, (100, 100, 100), (px, py, pw, ph), 2)

        pause_text  = self.font_mid.render("PAUSED", True, WHITE)
        resume_text = self.font.render("Press SPACE to resume", True, (90, 90, 90))
        self.screen.blit(pause_text,  (cx - pause_text.get_width()  // 2, py + 30))
        self.screen.blit(resume_text, (cx - resume_text.get_width() // 2, py + 90))

    def _draw_menu(self):
        # Dark background with faint grid lines
        self.screen.fill((20, 20, 20))
        for col in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, (32, 32, 32),
                             (col * CELL_SIZE, 0), (col * CELL_SIZE, SCREEN_HEIGHT))
        for row in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, (32, 32, 32),
                             (0, row * CELL_SIZE), (SCREEN_WIDTH, row * CELL_SIZE))

        # Background snake
        visible = [(x, y) for x, y in self.menu_snake_cells
                   if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT]
        if visible:
            hx, hy = self.menu_snake_cells[0]
            head_vis = (0 <= hx < GRID_WIDTH and 0 <= hy < GRID_HEIGHT)
            draw_snake_body(self.screen, visible, self.menu_snake_dir,
                            GREEN, DARK_GREEN, show_head=head_vis)

        # Title with drop shadow
        shadow_surf = self.font_large.render("Snake, but better.", True, (0, 70, 0))
        title_surf  = self.font_large.render("Snake, but better.", True, WHITE)
        tx = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        self.screen.blit(shadow_surf, (tx + 3, 143))
        self.screen.blit(title_surf,  (tx, 140))

        # Styled mode buttons
        btn_w, btn_h = 270, 52
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2

        # Classic — dark green box with raised border
        cy = 255
        pygame.draw.rect(self.screen, (12, 45, 12), (btn_x, cy, btn_w, btn_h))
        pygame.draw.line(self.screen, (0, 180, 0), (btn_x, cy), (btn_x + btn_w, cy), 2)
        pygame.draw.line(self.screen, (0, 180, 0), (btn_x, cy), (btn_x, cy + btn_h), 2)
        pygame.draw.line(self.screen, (0, 60, 0), (btn_x + btn_w, cy), (btn_x + btn_w, cy + btn_h), 2)
        pygame.draw.line(self.screen, (0, 60, 0), (btn_x, cy + btn_h), (btn_x + btn_w, cy + btn_h), 2)
        classic_lbl = self.font_mid.render("1   Classic", True, GREEN)
        self.screen.blit(classic_lbl, (btn_x + btn_w // 2 - classic_lbl.get_width() // 2,
                                       cy + btn_h // 2 - classic_lbl.get_height() // 2))

        # Twisted — dark purple box with raised border
        cy = 325
        pygame.draw.rect(self.screen, (35, 10, 55), (btn_x, cy, btn_w, btn_h))
        pygame.draw.line(self.screen, (150, 50, 255), (btn_x, cy), (btn_x + btn_w, cy), 2)
        pygame.draw.line(self.screen, (150, 50, 255), (btn_x, cy), (btn_x, cy + btn_h), 2)
        pygame.draw.line(self.screen, (50, 0, 100), (btn_x + btn_w, cy), (btn_x + btn_w, cy + btn_h), 2)
        pygame.draw.line(self.screen, (50, 0, 100), (btn_x, cy + btn_h), (btn_x + btn_w, cy + btn_h), 2)
        twisted_lbl = self.font_mid.render("2   Twisted", True, (180, 80, 255))
        self.screen.blit(twisted_lbl, (btn_x + btn_w // 2 - twisted_lbl.get_width() // 2,
                                       cy + btn_h // 2 - twisted_lbl.get_height() // 2))

        # Hint
        hint = self.font.render("Press 1 or 2 to choose a mode", True, (90, 90, 90))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 460))

        pause_hint = self.font.render("Press SPACE to pause", True, (60, 60, 60))
        self.screen.blit(pause_hint, (SCREEN_WIDTH // 2 - pause_hint.get_width() // 2, 490))

        # Glow on the selected button while waiting for sound to finish
        if self.fade_pending_mode and self.fade_delay > 0:
            glow_cy   = 255 if self.fade_pending_mode == "classic" else 325
            glow_col  = (0, 220, 0) if self.fade_pending_mode == "classic" else (170, 60, 255)
            glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for i, alpha in enumerate([60, 35, 15]):
                pad = (i + 1) * 4
                pygame.draw.rect(glow_surf, (*glow_col, alpha),
                                 (btn_x - pad, glow_cy - pad,
                                  btn_w + pad * 2, btn_h + pad * 2), 2)
            # Bright solid inner border on top
            pygame.draw.rect(self.screen, glow_col,
                             (btn_x - 2, glow_cy - 2, btn_w + 4, btn_h + 4), 2)
            self.screen.blit(glow_surf, (0, 0))

        # Fade to black overlay
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, self.fade_alpha))
            self.screen.blit(fade_surf, (0, 0))

    def _draw_game_over(self):
        cx = self.screen_w // 2
        cy = self.screen_h // 2

        # Dark translucent overlay over the frozen game frame
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))

        # Stats panel
        pw, ph = 300, 190
        px, py = cx - pw // 2, cy - ph // 2
        pygame.draw.rect(self.screen, (18, 18, 18), (px, py, pw, ph))
        pygame.draw.rect(self.screen, (200, 50, 50), (px, py, pw, ph), 2)

        over_text  = self.font_mid.render("GAME  OVER", True, (220, 60, 60))
        self.screen.blit(over_text, (cx - over_text.get_width() // 2, py + 18))

        # Divider
        pygame.draw.line(self.screen, (60, 20, 20),
                         (px + 16, py + 62), (px + pw - 16, py + 62), 1)

        score_text = self.font.render("Score    " + str(self.score), True, WHITE)
        best_text  = self.font.render("Best     " + str(self.high_score), True, GOLD)
        self.screen.blit(score_text, (cx - score_text.get_width() // 2, py + 76))
        self.screen.blit(best_text,  (cx - best_text.get_width()  // 2, py + 106))

        retry_text = self.font.render("Press R to return to menu", True, (90, 90, 90))
        self.screen.blit(retry_text, (cx - retry_text.get_width() // 2, py + ph - 34))

        # Red flash — drawn last so it sits on top while fading out
        if self.death_flash_timer > 0:
            alpha = int(210 * (self.death_flash_timer / 0.4))
            flash = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
            flash.fill((200, 0, 0, alpha))
            self.screen.blit(flash, (0, 0))

    def run(self):
        # The main game loop — keeps running until the window is closed
        running = True
        while running:
            dt = self.clock.tick_busy_loop(FPS) / 1000.0  # time since last frame in seconds
            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
