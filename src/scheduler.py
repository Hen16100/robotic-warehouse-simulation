from typing import List, Optional, Tuple
from robot import Robot
from warehouse import Warehouse
from pathfinding import a_star
import math

def fifo_allocate(warehouse: Warehouse, robots: List[Robot], width: int, height: int):
    assigned = []
    for robot in robots:
        if robot.state == 'idle':
            unassigned = warehouse.list_unassigned()
            if not unassigned:
                break
            task = unassigned[0]
            warehouse.tasks.remove(task)
            task.status = 'assigned'
            pickup_pos = task.pickup
            dropoff_pos = task.dropoff
            p1 = a_star(robot.pos, pickup_pos, width, height) if pickup_pos else []
            p2 = a_star(pickup_pos, dropoff_pos, width, height) if (pickup_pos and dropoff_pos) else []
            robot.assign_task(task, p1, p2)
            assigned.append((robot.id, task.id))
    return assigned

def nearest_allocate(warehouse: Warehouse, robots: List[Robot], width: int, height: int):
    assigned = []
    for robot in robots:
        if robot.state != 'idle':
            continue
        tasks = warehouse.list_unassigned()
        if not tasks:
            continue
        best = None
        best_dist = math.inf
        for t in tasks:
            if t.pickup is None:
                continue
            d = abs(robot.pos[0] - t.pickup[0]) + abs(robot.pos[1] - t.pickup[1])
            if d < best_dist:
                best_dist = d
                best = t
        if best:
            warehouse.tasks.remove(best)
            best.status = 'assigned'
            p1 = a_star(robot.pos, best.pickup, width, height)
            p2 = a_star(best.pickup, best.dropoff, width, height) if best.dropoff else []
            robot.assign_task(best, p1, p2)
            assigned.append((robot.id, best.id))
    return assigned