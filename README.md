<div align="center">
  <img src="icon.png" alt="AI Cargo Pathfinder Logo" width="200"/>
  <h1>🤖 AI Cargo Pathfinder</h1>
  <p><strong>A Next-Generation Autonomous Warehouse Robot Simulation built with Panda3D and Bullet Physics.</strong></p>
  <p>
    <a href="#overview">Overview</a> •
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage--controls">Usage</a> •
    <a href="#github-deployment-guide">GitHub Deployment</a>
  </p>
</div>

---

## 📖 Overview

Welcome to the **AI Cargo Pathfinder** project! This is a highly sophisticated, self-contained 3D simulation of an autonomous warehouse robotics system. Built using Python, the **Panda3D Game Engine**, and the **Bullet Physics Engine**, this project demonstrates how to build a robust physics-driven AI environment completely from scratch.

Unlike many projects that rely on gigabytes of external 3D models (like `.obj` or `.gltf` files) or complex game engines (like Unity or Unreal), the AI Cargo Pathfinder generates **100% of its environment procedurally through mathematical code**. This ensures the project is lightweight, lightning-fast to boot, and incredibly easy to understand at a source-code level.

Whether you are a student looking to understand 3D rendering, a robotics enthusiast exploring LiDAR simulations, or a developer wanting to see an elegant Python-based Finite State Machine (FSM) in action, this project serves as a perfect foundational template.

---

## ✨ Features

### 1. Procedural 3D Geometry
The entire warehouse—the floor, the towering walls, the wooden crates, the heavy metal storage shelves, and the robot itself—is generated at runtime. 
* We utilize Panda3D's `GeomVertexData` to define vertices, normals, and color vectors.
* By doing this, we eliminate the need for external asset loading, making the application highly portable and removing the risk of "missing file" errors.

### 2. Bullet Physics Engine Integration
Movement in this simulation is not faked by simply changing X/Y coordinates. Every object is a physical entity governed by Earth's gravity (`-9.81 m/s²`).
* **Static Environment**: The floor, walls, and obstacles are static `BulletBoxShape` nodes with infinite mass. They cannot be moved, providing a rigid boundary for the simulation.
* **Dynamic Robot**: The robot is a `BulletCylinderShape` with an assigned mass of `80kg`. Movement is achieved by applying linear and angular velocities to its `BulletRigidBodyNode`.

### 3. Simulated LiDAR Sensor Array
The core of the robot's perception system is a simulated LiDAR (Light Detection and Ranging) array.
* The robot casts **7 distinct physics raycasts** spanning a 120-degree Field of View in front of it.
* Every frame, the physics engine calculates the exact intersection point between these invisible rays and the solid geometry of the warehouse.
* The system returns the exact distance to the nearest obstacle, allowing the robot to "see" the world mathematically.
* **Visual Debugging**: You can press `F1` to visualize these invisible rays. They dynamically change color (Green for safe, Yellow for caution, Red for danger) based on the proximity of obstacles.

### 4. Autonomous Finite State Machine (FSM) AI
The robot possesses a built-in "brain" that allows it to navigate the warehouse infinitely without getting stuck.
* **Drive Forward**: The default state. The robot moves straight ahead while polling its LiDAR sensors.
* **Scan**: If the central sensors detect a wall or crate within the 1.5-meter critical zone, the robot stops. It then compares the distance readings on its left sensors versus its right sensors to determine which direction has more open space.
* **Turn/Avoid**: The robot applies angular torque to turn in the optimal direction until the central path is clear again, seamlessly transitioning back to the Drive Forward state.

### 5. Custom Real-Time HUD
A built-in telemetry system overlays critical data directly onto the 3D viewport.
* Built using Panda3D's `OnscreenText` framework.
* Displays the current operating mode (Manual vs. Autonomous).
* Streams the live distance readings (in meters) of all 7 LiDAR sensors.
* Flashes high-visibility warnings when an imminent collision is detected.

---

## 🏗️ Technical Architecture & Codebase Breakdown

The codebase is meticulously organized into a `core` package to ensure maintainability and separation of concerns.

### `main.py`
The entry point of the application. It handles crucial environment setup, specifically forcing the Windows command line (`sys.stdout`) to use UTF-8 encoding. This prevents the application from crashing when trying to print advanced HUD telemetry characters to a standard `cmd.exe` or PowerShell terminal. It then instantiates and runs the `WarehouseSimulationApp`.

### `core/constants.py`
The single source of truth for the simulation's "magic numbers". It defines the window resolution, physics gravity vectors, LiDAR ray angles, robot speed, critical detection distances, and the RGB color palette used for procedural generation.

### `core/procedural_geo.py`
The mathematical heart of the visuals. It contains the low-level functions that construct raw 3D meshes. 
* `create_procedural_box()`: Calculates the 8 corners of a cube and weaves them into 12 distinct triangles.
* `create_procedural_cylinder()`: Uses Sine and Cosine trigonometry to generate a smooth cylindrical body for the robot.
* `create_line_node()`: Generates simple 3D line segments used for visualizing the LiDAR rays.

### `core/environment.py`
The architect of the warehouse. It utilizes the functions from `procedural_geo.py` to assemble the scene. It lays down the floor, erects the boundary walls, and iterates through a predefined list of coordinates to spawn the obstacle crates and shelves. It also configures the global ambient and directional lighting to give the scene physical depth and shadows.

### `core/physics.py`
The manager of the Bullet Physics world. It sets up the invisible collision world that runs parallel to the visual 3D world. It also provides the `BulletDebugNode` which allows developers to visualize the raw collision hitboxes.

### `core/robot.py`
This module defines the `RobotController`. It marries the procedural cylinder visual to the `BulletRigidBodyNode`. It handles the keyboard input for Manual driving (applying velocity vectors based on the camera angle) and encapsulates the FSM logic required for Autonomous mode.

### `core/sensors.py`
The `SensorArray` class. It attaches to the front of the robot and acts as its eyes. It performs the complex matrix math required to offset the raycasts based on the robot's current heading (Yaw), interacts with the physics world to perform the `rayTestClosest` calls, and updates the colorful debug visualization lines.

### `core/hud.py`
The 2D user interface overlay. It manages the Panda3D `aspect2d` scene graph to render text that remains pinned to the screen regardless of where the 3D camera is looking.

### `core/app.py`
The grand orchestrator. It subclasses Panda3D's `ShowBase`. It initializes the window, sets up the camera angle, and instantiates the Environment, PhysicsManager, RobotController, and HUD, linking them all together into the primary simulation loop.

---

## 🚀 Installation & Setup

### Prerequisites
You will need **Python 3.9 or higher** installed on your system.

### Option 1: Running from Source
If you want to view, edit, or modify the Python code:

1. Clone or download this repository to your local machine.
2. Open a terminal (Command Prompt, PowerShell, or bash).
3. Navigate to the project directory:
   ```bash
   cd "path/to/AI Cargo Pathfinder"
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the simulation:
   ```bash
   python main.py
   ```

### Option 2: Running the Standalone Executable (.exe)
If you simply want to play the simulation without installing Python or any libraries, a pre-compiled Windows executable is available!

1. Navigate to the `dist/AICargoPathfinder/` folder.
2. Double-click **`AICargoPathfinder.exe`**.
3. That's it! The game will launch immediately.

*(Note: The executable contains the entire Python interpreter, the Panda3D engine, and the Bullet physics library, which is why the folder is relatively large ~140MB).*

---

## 🎮 Usage & Controls

Once the simulation is running, use the following keys to interact with the robot:

| Key | Action | Description |
|:---:|:---|:---|
| **SPACE** | **Toggle AI Mode** | Switches the robot between Manual Control and Autonomous AI navigation. |
| **W / Up Arrow** | **Drive Forward** | Applies forward linear velocity to the robot (Manual mode only). |
| **S / Down Arrow** | **Drive Reverse** | Applies reverse linear velocity to the robot (Manual mode only). |
| **A / Left Arrow** | **Steer Left** | Applies counter-clockwise angular velocity to rotate the robot left. |
| **D / Right Arrow** | **Steer Right** | Applies clockwise angular velocity to rotate the robot right. |
| **R** | **Reset** | Instantly teleports the robot back to its starting coordinate `(0, -10, 1)`. |
| **F1** | **Toggle Debug** | Turns on the Bullet Physics wireframes and renders the 7 LiDAR sensor rays. |
| **ESC** | **Quit** | Gracefully closes the simulation and the console. |

---

## 🌐 GitHub Deployment Guide

Are you ready to showcase this project to employers or fellow developers on GitHub? Follow this step-by-step guide to upload the AI Cargo Pathfinder!

### 1. The `.gitignore` File (Already Included!)
When uploading a project to GitHub, you **do not** want to upload temporary cache files, virtual environments, or massive compiled `.exe` files. This project already includes a perfectly configured `.gitignore` file. 

**What it ignores:**
* `__pycache__/` and `*.pyc` files (Python compilation artifacts).
* `build/` and `dist/` folders (The 140MB+ folders created by PyInstaller).
* `.venv/` (Your local Python virtual environment).

Because of this file, when you upload the project, GitHub will only store the lightweight, clean Python source code (`.py` files), making your repository professional and quick to download.

### 2. The License (MIT License)
When creating a public repository, you should select a License so others know how they can use your code. 

This project currently includes the **MIT License**.
* **Why MIT?** The MIT License is the most popular open-source license in the world. It is highly permissive. It allows anyone to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of the software, as long as they include the original copyright notice. 
* **Recommendation:** When you upload this to GitHub, keep the `LICENSE` file as is. It shows employers you understand standard open-source practices.

### 3. Step-by-Step Upload Instructions

If you haven't already, download and install [Git for Windows](https://git-scm.com/download/win).

1. **Initialize the Repository**
   Open your terminal in the project folder and run:
   ```bash
   git init
   ```
2. **Add Your Files**
   Tell Git to track all the files in the directory (the `.gitignore` will automatically filter out the bad ones):
   ```bash
   git add .
   ```
3. **Commit Your Code**
   Save this version of the code with a descriptive message:
   ```bash
   git commit -m "Initial commit: Complete AI Cargo Pathfinder Simulation"
   ```
4. **Create a Repository on GitHub.com**
   * Go to your [GitHub profile](https://github.com/) and click **New Repository**.
   * Give it a name (e.g., `ai-cargo-pathfinder`).
   * Add a short description (e.g., *Autonomous Warehouse Robot Simulation built with Panda3D*).
   * Leave it Public.
   * **Do NOT** check the boxes to add a README, .gitignore, or License (since we already have them locally!).
   * Click **Create repository**.
5. **Link and Push**
   GitHub will show you a page with instructions. Look for the section titled **"…or push an existing repository from the command line"**. Copy those three lines and paste them into your terminal. They will look something like this:
   ```bash
   git remote add origin https://github.com/YourUsername/AI-Cargo-Pathfinder.git
   git branch -M main
   git push -u origin main
   ```
6. **Success!**
   Refresh your GitHub page. Your beautiful Python code, this massive README, your custom icon, and your clean commit history will be visible for the world (and future employers) to see!

---

<div align="center">
  <p>Built with ❤️ using <a href="https://www.panda3d.org/">Panda3D</a> & <a href="https://pybullet.org/">Bullet Physics</a>.</p>
</div>
