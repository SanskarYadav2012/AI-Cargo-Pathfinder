# Sensors and LiDAR

## Simulated Sensor Array (`core/sensors.py`)
To mimic a real-world autonomous robot, the `SensorArray` class implements a simulated LiDAR (Light Detection and Ranging) system. 

It generates 7 rays fanning out from the front of the robot. The angles of these rays cover a 120-degree field of view (e.g., -60°, -40°, -20°, 0°, +20°, +40°, +60°).

## The Raycast Mechanism
During every physics frame, the sensor array calls `world.rayTestClosest(start_pos, end_pos)`.
1. **Start Position**: The center of the robot.
2. **End Position**: A point calculated 10 meters away along the specific angle of the ray.

The Bullet physics engine traces this imaginary line through the 3D space. If it hits a rigid body (a shelf, a crate, or a wall), it returns a `BulletRayHit` object containing:
- The exact 3D coordinate of the impact.
- The physics node that was hit.
- The normal vector of the surface hit.

The sensor array calculates the distance from the robot to the hit point and stores this data.

## Visualization
To aid debugging and visualization, the sensor rays are drawn dynamically using 3D line segments (generated in `procedural_geo.py`). 
- If a ray hits an object within the danger zone, the line is colored **Red**.
- If a ray hits an object further away, the line is colored **Yellow**.
- If a ray hits nothing, it is colored **Green**.

This visualization, along with the physics wireframes, can be toggled using the **F1** key.
