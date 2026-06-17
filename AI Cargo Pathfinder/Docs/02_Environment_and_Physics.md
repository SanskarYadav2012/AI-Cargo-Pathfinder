# Environment and Procedural Geometry

## Procedural Geometry (`core/procedural_geo.py`)
To keep the application entirely self-contained without needing 3D modelling software (like Blender), the game generates all its meshes via code.

Panda3D builds 3D shapes using `GeomVertexData`. The `procedural_geo.py` module contains helper functions that construct the required primitives mathematically:
- **`create_procedural_box`**: Defines 8 vertices of a cube, then creates 12 triangles (2 per face) mapped to a specific color. Used for the floor, walls, shelves, and crates.
- **`create_procedural_cylinder`**: Uses trigonometry (`sin` and `cos`) to generate a circle of vertices along a Z-axis. It builds a triangle fan for the top and bottom caps, and quads for the sides. Used for the robot body.
- **`create_line_node`**: Generates a 3D line segment, primarily used to visualize the LiDAR sensor rays.

## The Warehouse Environment (`core/environment.py`)
The `WarehouseEnvironment` class is responsible for assembling the static scene.

1. **Floor & Walls**: It creates a large flat box for the floor. Four long boxes are placed at the edges to act as solid walls, keeping the robot contained.
2. **Obstacles**: It iterates through a predefined list of positions, dimensions, and colors (defined in `constants.py`) to spawn "shelves" and "crates" across the warehouse floor.
3. **Lighting**: It sets up an `AmbientLight` to illuminate the entire scene softly, and a `DirectionalLight` to cast shadows and provide depth/shading to the 3D objects, giving them a physical, solid look.

## Bullet Physics Integration (`core/physics.py`)
The game uses the **Bullet Physics Engine** (integrated into Panda3D via `panda3d.bullet`). 

- The `PhysicsManager` initializes a `BulletWorld` and sets gravity to `(0, 0, -9.81)` to mimic Earth.
- Every physical object in the environment (floor, walls, obstacles) has a `BulletBoxShape`.
- These static objects are assigned a mass of `0`, which tells the physics engine that they cannot be moved by collisions.
- The physics manager also provides a `BulletDebugNode`, which can be toggled on/off (using the F1 key) to visualize the invisible collision meshes overlapping the visual 3D models.
