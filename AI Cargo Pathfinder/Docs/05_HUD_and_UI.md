# HUD and User Interface

## Telemetry Display (`core/hud.py`)
The game requires a way to feedback data to the user without relying solely on the console. The `HUD` class handles all 2D text rendered on top of the 3D scene.

It uses Panda3D's `OnscreenText` utility to render crisp, high-resolution text locked to the 2D screen coordinate system (`aspect2d`).

### Features of the HUD
1. **State Banner**: At the top left, a banner displays the current control mode: `[MANUAL CONTROL]` or `[AUTONOMOUS AI]`. The text color dynamically changes (Cyan for Manual, Green for Autonomous) to give clear visual feedback.
2. **Sensor Readout**: In the top right, a block of text prints out the exact distance detected by the 7 LiDAR rays in real-time. This allows the user to see exactly what the robot "sees" mathematically.
3. **Control Legend**: At the bottom of the screen, a static block of text reminds the user of the available keyboard controls (Movement, Toggle Mode, Reset, Debug).
4. **Collision Warnings**: If the central sensor detects an obstacle within critical range, a `[ COLLISION WARNING ]` flashes on the screen in red.

## Handling Encoding
A notable technical challenge with the UI and console output is text encoding. Standard Windows console (`cmd` or PowerShell) often defaults to `cp1252` encoding. If the script attempts to print advanced Unicode characters (like box-drawing characters `╔` or warning symbols `⚠`), the application will crash with a `UnicodeEncodeError`.

To solve this:
1. `main.py` explicitly forces Python to use UTF-8 for `sys.stdout` and `sys.stderr`.
2. The HUD text is sanitized to use standard ASCII brackets and characters to guarantee 100% compatibility across all systems.
