# settings.py
# All game constants live here.

# --- Screen ---
SCREEN_WIDTH  = 600
SCREEN_HEIGHT = 600
TITLE         = "Snake, but better."
FPS           = 120         # frames per second — how smooth the game runs

# --- Grid ---
# The game world is divided into a grid of cells.
# Each cell is CELL_SIZE x CELL_SIZE pixels.
# The snake, food, and obstacles all snap to this grid.
CELL_SIZE     = 30          # pixels per grid cell
GRID_WIDTH    = SCREEN_WIDTH  // CELL_SIZE   # 20 cells across
GRID_HEIGHT   = SCREEN_HEIGHT // CELL_SIZE   # 20 cells tall

# --- Twisted mode arena (larger than Classic) ---
# 780 / 30 = 26 cells across and tall — 6 extra cells per side vs Classic
TWISTED_SCREEN_WIDTH  = 780
TWISTED_SCREEN_HEIGHT = 780
TWISTED_GRID_WIDTH    = TWISTED_SCREEN_WIDTH  // CELL_SIZE   # 26 cells across
TWISTED_GRID_HEIGHT   = TWISTED_SCREEN_HEIGHT // CELL_SIZE   # 26 cells tall

# --- Snake ---
SNAKE_SPEED        = 8     # cells per second (base speed)
SPEED_BOOST_MULT   = 1.5    # speed multiplier when boost power-up is active
SLOW_DOWN_MULT     = 0.5    # speed multiplier when slow-down power-up is active
INITIAL_LENGTH     = 3      # how many segments the snake starts with
SHRINK_AMOUNT      = 3      # how many segments the shrink power-up removes

# --- Power-ups ---
POWERUP_DURATION        = 5.0   # seconds a timed power-up lasts (default)
SPEED_BOOST_DURATION    = 10.0   # seconds speed boost lasts
MAGNET_DURATION         = 10.0   # seconds magnet lasts
POWERUP_SPAWN_RATE      = 10.0  # seconds between power-up spawns
DECOY_DURATION          = 15.0  # seconds before split decoy segments disappear
PORTAL_DURATION         = 15.0  # seconds portals stay active
MAGNET_RANGE            = 3     # Manhattan distance at which food gets pulled toward the head

# --- Random events ---
EVENT_COOLDOWN          = 12.0  # seconds between events (starts after previous event fully ends)
OBSTACLE_CHUNK_INTERVAL = 1.3   # seconds between each chunk spawning / despawning
OBSTACLE_MAX_CHUNKS     = 6     # total chunks per obstacle wave
OBSTACLE_ACTIVE_TIME    = 4.0   # seconds all chunks stay fully on the grid
OBSTACLE_MIN_CELLS      = 2     # minimum cells per chunk
OBSTACLE_MAX_CELLS      = 4     # maximum cells per chunk
ANACONDA_LENGTH         = 50    # number of cells in the anaconda body
ANACONDA_SPEED          = 0.2   # seconds per step (5 cells/second)
HORDE_MIN_COUNT         = 5     # minimum baby snakes per horde
HORDE_MAX_COUNT         = 6     # maximum baby snakes per horde
HORDE_SNAKE_MIN_LEN     = 2     # minimum cells per baby snake
HORDE_SNAKE_MAX_LEN     = 3     # maximum cells per baby snake
HORDE_SPEED             = 0.15  # seconds per step (~6.7 cells/second)
HORDE_WARNING_TIME      = 2.0   # seconds of warning before snakes enter
HORDE_VULNERABLE        = 7     # segments from head that are vulnerable to horde

# --- Food ---
REGULAR_FOOD_POINTS = 1
BONUS_FOOD_POINTS   = 5
BONUS_FOOD_DURATION = 7.0   # seconds before bonus food disappears

# --- Colors (R, G, B) ---
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
GRAY        = (40,  40,  40)    # background
DARK_GRAY   = (60,  60,  60)    # grid lines

GREEN       = (0,   200, 0)     # snake body
DARK_GREEN  = (0,   150, 0)     # snake head

RED         = (220, 50,  50)    # regular food
GOLD        = (255, 200, 0)     # bonus food

BLUE        = (50,  150, 255)   # speed boost power-up
CYAN        = (0,   220, 220)   # slow down power-up
PURPLE      = (180, 0,   255)   # double points power-up
ORANGE      = (255, 140, 0)     # shrink power-up

WHITE_GRAY      = (180, 180, 180)   # obstacles

# --- Grid tile colors ---
CLASSIC_CELL_A  = (42,  52,  42)    # classic mode checkerboard — lighter green-gray
CLASSIC_CELL_B  = (36,  45,  36)    # classic mode checkerboard — darker green-gray
TWISTED_CELL_A  = (38,  32,  55)    # twisted mode checkerboard — lighter dark-purple
TWISTED_CELL_B  = (30,  25,  45)    # twisted mode checkerboard — darker dark-purple
MYSTERY         = (220, 0,   220)   # mystery box
DECOY           = (120, 180, 120)   # split decoy segments (faded snake green)
PORTAL_COLOR    = (150, 50,  255)   # portal rings
ANACONDA_BODY   = (140, 70,  0)     # anaconda body segments
ANACONDA_HEAD_C = (220, 110, 0)     # anaconda head (brighter)
BABY_SNAKE      = (200, 0,   0)     # horde baby snake body
BABY_SNAKE_HEAD = (240, 30,  30)    # horde baby snake head (brighter red)
VULNERABLE      = (255, 215, 0)     # gold highlight for vulnerable snake segments

# --- Game States ---
# The game is always in exactly one of these states.
STATE_MENU      = "menu"
STATE_PLAYING   = "playing"
STATE_PAUSED    = "paused"
STATE_GAME_OVER = "game_over"

# --- Files ---
HIGH_SCORE_FILE = "highscore.json"