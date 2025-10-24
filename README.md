# Robotic Warehouse Simulation

## Overview
This project simulates an agent-based robotic warehouse system using discrete-event simulation. It models robots, shelves, and customer orders to analyze task allocation, routing, and system performance.

Each simulation run will generate a JSON file, a CSV file, and a visual animation in the form of a GIF, showing the robots performing their task.

## Repository Structure
- `main.py` - main simulation entry point
- `src/` - Python classes for Warehouse, Robot, Order, Shelf, Task
- `diagrams/` - UML diagrams (PlantUML)
- `docs/` - proposal PDF and future reports
- `data/` - logs and metrics

## Status

**Implemented (M1)**
- Initial repository setup with project structure and placeholder files.


**Implemented (M2)**
- Core simulation skeleton and world
- Robot entity class with path following
- Two task allocation strategies
    - FIFO queue
    - Nearest-Neighbor greedy
- A* pathfinding for movement
- CLI runner to launch scenarios
- CSV output for each runner
- Unit tests for core components
- Basic logging/data collection mechanisms


**Milestone 3 (Complete implementation)**
- Completed full simulation logic
- Added collision avoidance using robot priority
- Robots now avoid shelves and other robots
- Implemented a multi-run execution
- Added data collection in CSV
- Added visualization output
- Extended warehouse with configurable size, number of shelves, robots, and tasks
- Integrated performance metrics such as robot utilization and step count


## Simulation Features
| Feature | Description |
|----------|--------------|
| **Task Allocation** | FIFO or nearest-shelf heuristic. |
| **Pathfinding** | A* algorithm avoiding shelves and occupied cells. |
| **Collision Avoidance** | Priority-based movement scheduling (robot 1 > robot 2 > ...). |
| **Visualization** | Matplotlib animation showing robots, shelves, and paths. |
| **Data Logging** | Exports detailed step-by-step logs and summary reports. |
| **Parameterization** | Width, height, number of robots, steps, and random seed configurable. |


## Data Output
Each simulation run produces:
- **`run_###.csv`** – Time-series log of robot position, state, and task.
- **`run_###_summary.json`** – Summary statistics for that run.
- **`run_###.gif`** – Visualization of the robot movement.


Example:
```json
{
    "run_id": 3,
  "steps": 142,
  "duration_s": 1.97,
  "nrobots": 5,
  "ntasks": 10,
  "robot_utilization": { "1": 98, "2": 105, "3": 92, "4": 100, "5": 87 }
}
```

## Installation
Requirements: Python 3.10+ (3.9 may work)
1. Clone repo
2. Create venv:
```bash
python -m venv venv
source venv/bin/activate    # Unix
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## How to run
For a single simulation:
```python
python main.py
```

To run 10 simulations with different seeds:
```python
from main import RunManager

manager = RunManager(
    width=15,
    height=12,
    nrobots=3,
    ntasks=6,
    steps=200,
    algo='fifo',
    seed=42
)
manager.run_multiple(runs = 10)
```
To run with custom parameters:
```python
manager = RunManager(width=xx, height=xx, nrobots=x, ntasks=xx, algo='xxx', seed=xx)
manager.run_single(run_id=1)
```

