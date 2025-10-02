# Robotic Warehouse Simulation

## Overview
This project simulates an agent-based robotic warehouse system using discrete-event simulation. It models robots, shelves, and customer orders to analyze task allocation, routing, and system performance.

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

**Planned (M3 / later)**
- More sophosticated task allocations
- Collision avoidance and multi-robot path coordination
- Visualization using SimPy, Matplot, and NetworkX
- Performance evaluation and plots
- CI and packaging
- Extended test-suite and sample scenarios

**Changes from proposal**
- Implemented Nearest-Neighbor allocator in addition to FIFO
- A* chosen for path planning now

## Installation
Requirements: Python 3.10+ (3.9 may work)
1. Clone repo
2. Create venv:
```bash
python -m venv venv
source venv/bin/activate    # Unix
venv\Scripts\activate   # Windows
pip install -r requirements.txt
