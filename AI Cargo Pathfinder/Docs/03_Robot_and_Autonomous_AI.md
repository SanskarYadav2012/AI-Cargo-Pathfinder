# Robot and Autonomous AI

## Robot Physical Properties (`core/robot.py`)
The `RobotController` manages the player/AI entity in the simulation. 
- **Visuals**: The robot is rendered as an orange procedural cylinder with a distinct "front indicator" box to show which way it is facing.
- **Physics**: It uses a `BulletCylinderShape`. Unlike the environment, the robot has a mass of `80 kg`, making it dynamic. 
- **Constraints**: To prevent the cylindrical robot from falling over like a rolling pin, its `AngularFactor` is locked to `(0, 1, 0)`. This means physics collisions can only rotate it horizontally (yaw), not pitch or roll.

## Manual Control
In manual mode, the user drives the robot using W/A/S/D or Arrow keys.
- **W / S**: Applies a linear velocity force relative to the robot's current forward-facing vector.
- **A / D**: Applies angular velocity (rotation) directly to the body.
Because movement is handled via setting velocities on the `BulletRigidBodyNode`, collisions with walls and obstacles feel natural and solid.

## Autonomous AI (Finite State Machine)
When the user presses the `SPACE` bar, the robot enters Autonomous Mode. It utilizes a simple but highly effective Finite State Machine (FSM) to navigate:

### State 1: `STATE_DRIVE_FORWARD`
- The robot moves straight ahead at a constant speed.
- It continuously checks the LiDAR sensors. 
- If the central sensors detect an obstacle closer than the `CRITICAL_DISTANCE` (1.5 meters), the robot stops and transitions to the scanning state.

### State 2: `STATE_SCAN_OBSTACLE`
- The robot evaluates its LiDAR sensor array.
- It compares the distances detected on its left sensors versus its right sensors.
- If there is more open space on the right, it decides to turn right. Otherwise, it decides to turn left.
- It then transitions to the turning state.

### State 3: `STATE_TURN_AVOID`
- The robot applies angular rotation in the decided direction.
- It monitors the central sensors while turning. 
- Once the path straight ahead is clear (the central distance exceeds a safe threshold), it stops turning and transitions back to `STATE_DRIVE_FORWARD`.

This FSM loop ensures the robot can infinitely bounce around the warehouse, dynamically avoiding obstacles without a pre-programmed path.
