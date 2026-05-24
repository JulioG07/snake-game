Sprint 1 -- Core Mechanics
Date: May 24, 2026 

Goal
What was Sprint 1 supposed to accomplish?
The goal was to essencially to create the classic snake game before moving on with the twists! 
This invoved in creating our game loop to handle all events; a file to store all of our constants;
the snake class to create and manage its behaviors; and the food class to ensure our fruit was drawna and 
randonly spawn somewhere on the grid. 

What you completed
Which Trello cards / features actually got done?
- Github repo
- Create board & snake class
- Set game rules (collisions and point system)

What's still open
Anything you planned for Sprint 1 but didn't finish? (moves to next sprint)
All of Sprint 1 tasks got completed!

Challenges / bugs
What gave you trouble? Anything you got stuck on or had to fix?
At first it was understanding how all of these objects work together, so overall making sure
I clearly understood the OOP concepts being used in the game. 

What you learned
Any concept that clicked this sprint? 
- This was the first time I was Git branching and managing git pull requests
- The add-head/drop-tail movement
- Refresher on OPP concepts (e.g how self worked in this context)

Decisions made
Any choices worth noting?
- During office hours with David, we were dicussing wthever we should have the snake resemble a linkedlist or an array. Ended up choosing array because of its random acess properties (easier to check for self collisions)
- No unit testing will be done for this project
- For sprint 2, I wanna let the user pick between playing the classical snake game or its twisted version (Sprint 2) 

Next sprint
What's the focus for Sprint 2?
- Golden fruit (worth 5 points)
- Speedbost powerup
- Split decoy -- drops a fake stationary snake segment trail that obstacles target, disappears eventually
- Portal -- two linked portals appear; entering one teleports the head to the other
- Double point powerup 
- Bonus spawn -- instantly spawns 2-3 extra regular foods at once
- Magnet -- food within 1-2 cells gets pulled toward the snake's head.