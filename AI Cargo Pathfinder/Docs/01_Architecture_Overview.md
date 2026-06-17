# AI Cargo Pathfinder: Architecture Overview

## Introduction
The **AI Cargo Pathfinder** is a 3D warehouse simulation built using the **Panda3D Engine** and **Bullet Physics**. It is designed to demonstrate an autonomous robot navigating an obstacle-filled warehouse environment using simulated LiDAR sensors and a Finite State Machine (FSM).

## Core Philosophy
1. **Procedural First**: To ensure the project is highly portable and has zero external dependencies, no `.egg`, `.gltf`, or `.obj` files are used. Every 3D mesh (cubes, cylinders, lines) is procedurally generated at runtime using Panda3D's `GeomVertexData`.
2. **Physics-Driven Movement**: The robot and the environment are governed entirely by Bullet Physics. The robot isn't just teleported around; forces and velocities are applied to a `BulletRigidBodyNode`.
3. **Clean Code Architecture**: The code is split into logical modules to maintain a clean structure.

## Directory Structure
The codebase is organized into a main entry point and a `core` package:

```text
AI Cargo Pathfinder/
│
├── main.py                # The entry script. Handles UTF-8 console output and launches the app.
├── build_exe.py           # The PyInstaller script used to compile the standalone .exe.
├── README.md              # Project overview and quick-start guide.
├── icon.ico / icon.png    # The application icon.
│
└── core/                  # The main application package.
    ├── __init__.py        
    ├── app.py             # Contains the `WarehouseSimulationApp` ShowBase instance.
    ├── constants.py       # Global parameters, physics settings, and color palettes.
    ├── environment.py     # Generates the warehouse floor, walls, and obstacle shelves/boxes.
    ├── hud.py             # Manages the 2D OnscreenText elements (telemetry, mode, alerts).
    ├── physics.py         # Manages the BulletWorld and physics debug rendering.
    ├── procedural_geo.py  # Low-level mathematical generators for 3D meshes.
    ├── robot.py           # The robot body, physics constraints, and the Autonomous AI FSM.
    └── sensors.py         # The LiDAR raycasting system that detects distance to obstacles.
```

## How It All Connects
1. `main.py` instantiates `WarehouseSimulationApp` from `core/app.py`.
2. `WarehouseSimulationApp` sets up the Panda3D window, configures the camera, and initializes the `PhysicsManager`.
3. It then builds the `WarehouseEnvironment` (the static world).
4. Next, it spawns the `RobotController`, attaching it to the physics world.
5. It attaches the `SensorArray` to the robot's body.
6. Finally, it creates the `HUD` to display data and binds keyboard inputs.
7. During every frame (handled by Panda3D's Task Manager), the app steps the Bullet physics world, updates the robot's AI/movement, casts the sensor rays, and updates the HUD.
