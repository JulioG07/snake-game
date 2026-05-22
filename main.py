import pygame
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, GRAY


def main():
    # Start up pygame's internal systems (display, clock, etc.)
    pygame.init()

    # Create the window where everything is drawn.
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    # The clock controls how fast the game loop runs (FPS).
    clock = pygame.time.Clock()

    # --- The Game Loop ---
    # This runs over and over, many times per second, until the player quits.
    running = True
    while running:

        # 1. HANDLE EVENTS — check for input (key presses, window close, etc.)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:        # player clicked the window's X
                running = False

        # 2. UPDATE — game logic goes here later (move snake, check collisions...)
        #    Nothing yet.

        # 3. DRAW — paint the screen
        screen.fill(GRAY)            # clear screen to background color
        pygame.display.flip()        # show what we just drew

        # 4. CONTROL SPEED — wait so the loop runs at FPS, not as fast as possible
        clock.tick(FPS)

    # Loop ended — shut pygame down cleanly.
    pygame.quit()


# This runs main() only when you execute this file directly,
# not when it's imported by another file.
if __name__ == "__main__":
    main()