# Wumpus World: Logical Reasoning Agent

A web-based simulation of the classic **Wumpus World** AI problem. This project features an autonomous agent that uses propositional logic to navigate a dangerous 4x4 grid, avoid hazards, and retrieve gold.

## Overview
The Wumpus World is a testbed for intelligent agents. The agent must navigate a grid containing Pits and the deadly Wumpus beast. The agent makes decisions based on **Percepts**:
- **Breeze:** Adjacent to a Pit.
- **Stench:** Adjacent to the Wumpus.
- **Glitter:** In the same square as the Gold.

## Rules of the Game

### 1. The Environment
* **The Grid:** A 4x4 world (16 squares). The agent always starts at `(1,1)` facing Right.
* **Pits:** Each square (except the start) has a 20% chance of containing a Pit.
* **The Wumpus:** There is exactly one Wumpus hidden in the cave.
* **The Gold:** There is exactly one heap of Gold hidden in the cave.

### 2. Percepts (Sensory Inputs)
* **Stench:** In squares directly adjacent to the Wumpus (not diagonal).
* **Breeze:** In squares directly adjacent to a Pit (not diagonal).
* **Glitter:** In the square where the Gold is located.
* **Bump:** If the agent walks into a wall.
* **Scream:** Heard globally if the Wumpus is killed.

### 3. Agent Actions & Limitations
* **Movement:** The agent can move `Forward`, `Turn Left`, or `Turn Right`.
* **Shooting:** The agent has **only one arrow**. It travels in a straight line in the direction the agent is facing.
* **Grabbing:** The agent must manually "Grab" the gold when standing on the glitter square.
* **Climbing:** To win, the agent must return to `(1,1)` with the gold and "Climb" out.

### 4. Scoring System
* **+1000** for climbing out with the Gold.
* **-1000** for falling into a Pit or being eaten by the Wumpus.
* **-1** for every action taken (encourages efficiency).
* **-10** for using the Arrow.

## Logic Implementation
The agent maintains a **Knowledge Base (KB)** using propositional logic:
- `$OK_{x,y}$`: Cell is safe.
- `$V_{x,y}$`: Cell has been visited.
- `$¬P_{x,y}$`: Inferred that there is no Pit.

The agent uses a **Resolution-like** process to mark cells as `OK` only when it is certain no Pit or Wumpus exists there, based on the absence of Breezes and Stenches in neighboring visited cells.

## Tech Stack & Requirements
- **Language:** JavaScript (ES6+)
- **Library:** [p5.js v1.6.0](https://p5js.org/) (Loaded via CDN)
- **Environment:** Modern Web Browser (Chrome, Firefox, etc.)

## How to Run
1. Save the source code as `index.html`.
2. Ensure you have a stable internet connection (to load the p5.js library via CDN).
3. Open `index.html` in any web browser.
   - *Note: If using images, use a local server (e.g., VS Code Live Server) to avoid CORS issues.*

## Controls
| Action | Key |
| :--- | :--- |
| **Move Forward** | `Up Arrow` |
| **Turn Left/Right** | `Left/Right Arrows` |
| **Grab Gold** | `G` |
| **Shoot Arrow** | `S` |
| **Climb Out** | `C` |
| **Auto-Play** | `A` |
| **Reset Game** | `R` |
