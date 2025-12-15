## Author
Crystal

## Controls

- **W/A/S/D** - Move forward/left/backward/right relative to camera direction
- **Mouse** - Look around (first-person camera control)
- **R** - Generate a new maze
- **SPACE** - Reset player to starting position
- **ESC** - Exit game

## Game Mechanics

### Objective
Navigate from the starting position (0, 0) to the goal position (yellow/gold cube at the far corner) in the shortest time possible.

### Dead End System
The game features an intelligent dead end detection and warning system:

**Dead End Detection**
- A dead end is defined as any path with only one exit (excluding start and goal positions)
- The system looks ahead in your movement direction up to 6 units
- Detects if you're heading toward a dead end before you reach it

**Warning System**
- Red vignette effect appears on screen edges when heading toward a dead end
- Effect intensity increases the closer you get to the dead end
- Movement speed reduced to 50% when warning is active
- Warning fades when you change direction away from the dead end

**Penalty**
- If you physically enter a dead end cell, you're automatically reset to the starting position

### Power-Up System

**Launch Power-Up**
- Appears as a rotating cyan/blue diamond shape hovering above the ground
- Only one power-up exists per maze

**Effects**
- Launches player high above the maze for an aerial view
- 3-second smooth animation (1.5s up, 1.5s down)
- Camera automatically looks down during launch
- Maximum height: 15 units above ground
- Useful for scouting the maze layout

**Mechanics**
- Automatically activated when player moves within 0.4 units
- Can only be used once per maze
- New power-up spawns when a new maze is generated

### User Interface

**On-Screen Display**
- **Timer** (Bottom-left): Shows elapsed time in MM:SS format
- **Position** (Bottom-right): Shows current grid coordinates (X, Y)
- **Warning Effect**: Red vignette when approaching dead ends

**Console Output**
- New maze generation confirmation
- Reset position confirmation
- Goal reached with completion time
- Dead end penalty notification
- Power-up activation notification

## File Structure

```
maze_game.py          # Main game file
RiceFloor.png         # Optional floor texture (falls back to procedural)
WallGude.jpg          # Optional wall texture (falls back to procedural)
README.md             # This file
```

## Troubleshooting

**Textures not loading**
- Ensure texture files are in the same directory
- Check file names match exactly (case-sensitive on some systems)
- Game will use procedural textures as fallback

**Mouse not working**
- Ensure window has focus
- Try clicking inside the window
- Check if mouse events are being grabbed properly

Enjoy navigating the maze!
