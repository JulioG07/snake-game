Sprint 2 -- Twisted Mode & Powerups
Date: June 6, 2026

Goal
What was Sprint 2 supposed to accomplish?
The goal was to build out the full "Twisted" mode on top of the classic snake foundation.
This meant introducing a mystery box delivery system, a good/bad effect pool, and six
powerups that change how the game plays -- some helping the player, some actively working
against them.

What you completed
Which Trello cards / features actually got done?
- Classic vs Twisted mode selection on the main menu
- Larger Twisted arena (24x24 grid vs Classic's 20x20)
- Mystery box -- spawns every 8 seconds, player eats it to trigger a random effect
- 60/40 good/bad effect randomizer (two-stage: pick pool first, then pick effect)
- Golden fruit -- worth 5 points, spawned by the mystery box
- Speed boost -- snake moves 1.5x faster for 7 seconds
- Bonus spawn -- instantly places 2-3 extra food items on the grid
- Magnet -- food within 3 cells gets pulled one step toward the head each snake tick (7 seconds), with a pulsing cyan ring animation on in-range food
- Split decoy -- 30-50% of the snake's tail breaks off and becomes a stationary obstacle for 15 seconds; stacks if triggered twice before the timer runs out
- Portal -- two portals spawn at random grid positions; entering one teleports the head to the other, same direction, for 15 seconds

Challenges / bugs
What gave you trouble? Anything you got stuck on or had to fix?
- Split decoy was replacing the existing obstacle list instead of stacking onto it --
  caught when discussing a "second split in a row" scenario, fixed by swapping = for .extend()
- Portal teleport loop edge case: if two portals land adjacent and the snake moves between
  them, it would bounce infinitely. Fixed with a 2-step cooldown after each teleport.
- The game felt laggy even at 60 FPS, had to increase FPS

Decisions made
Any choices worth noting?
- Good/bad split moved from 70/30 to 60/40 to make Twisted mode feel riskier
- Portals assigned to BAD effects because random placement means the exit can drop the snake
  one step from a wall with no time to react
- All powerups delivered through a single mystery box rather than spawning independently --
  keeps the screen readable and powerup timing predictable
- Magnet and speed boost given their own 7-second duration constants instead of sharing
  the default POWERUP_DURATION, since they needed to feel meaningfully longer
- Decoy segments clear all at once when the timer expires (not per-segment) to keep the
  obstacle pattern readable

Next sprint
What's the focus for Sprint 3?
- Random Event generator: At random times throughout the game, I want the following four events to happen:
1. Random obstacule generation: a bunch of junk appers randoly throughout grid for x amount of time
2. Anaconda Generation: A huge anacando appraoches the grid and splits it in half horizontally, vertically, or diagnally. After x amount time, you can see the tail of the anancando leave the grid. 
3. Snake horde: A horde of baby snakes come to the grid on one direction.
- Sounds effects
- Eye Appealing UI & UX
