from typing import List
from robot import Robot
from warehouse import Warehouse
from pathfinding import a_star
import math

def fifo_allocate(warehouse: Warehouse, robots: List[Robot], width: int, height: int):
    assigned = []
    shelf_positions = [s.pos for s in warehouse.shelves.values()]
    next_positions = set()

    for robot in sorted(robots, key=lambda r: r.id):
        if robot.state != 'idle':
            if robot.state == 'to_pickup' and robot.path_to_pickup:
                next_positions.add(robot.path_to_pickup[0])
            elif robot.state == 'to_dropoff' and robot.path_to_dropoff:
                next_positions.add(robot.path_to_dropoff[0])
            continue
        unassigned = warehouse.list_unassigned()
        if not unassigned:
            break
        task = unassigned[0]
        warehouse.tasks.remove(task)
        task.status = 'assigned'
        obstacles = shelf_positions + list(next_positions)
        p1 = a_star(robot.pos, task.pickup, width, height, obstacles)
        p2 = a_star(task.pickup, task.dropoff, width, height, obstacles)
        if p2 is None:
            continue
        robot.assign_task(task, p1, p2)
        assigned.append((robot.id, task.id))
        if p1:
            next_positions.add(p1[0])
        elif p2:
            next_positions.add(p2[0])
    return assigned


def nearest_allocate(warehouse: Warehouse, robots: List[Robot], width: int, height: int):
    assigned = []
    shelf_positions = [s.pos for s in warehouse.shelves.values()]
    next_positions = set()
    for robot in sorted(robots, key=lambda r: r.id):
        if robot.state != 'idle':
            if robot.state == 'to_pickup' and robot.path_to_pickup:
                next_positions.add(robot.path_to_pickup[0])
            elif robot.state == 'to_dropoff' and robot.path_to_dropoff:
                next_positions.add(robot.path_to_dropoff[0])
            continue
        tasks = warehouse.list_unassigned()
        if not tasks:
            continue
        best_task = None
        best_dist = math.inf
        for t in tasks:
            if t.pickup is None:
                continue
            d = abs(robot.pos[0] - t.pickup[0]) + abs(robot.pos[1] - t.pickup[1])
            if d < best_dist:
                best_dist = d
                best_task = t
        if best_task:
            warehouse.tasks.remove(best_task)
            best_task.status = 'assigned'
            obstacles = shelf_positions + list(next_positions)
            p1 = a_star(robot.pos, best_task.pickup, width, height, obstacles)
            p2 = a_star(best_task.pickup, best_task.dropoff, width, height, obstacles)
            if p2 is None:
                continue
            robot.assign_task(best_task, p1, p2)
            assigned.append((robot.id, best_task.id))
            if p1:
                next_positions.add(p1[0])
            elif p2:
                next_positions.add(p2[0])
    return assigned
