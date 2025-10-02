import heapq
from typing import Tuple, List, Dict, Optional

Position = Tuple[int, int]

def heuristic(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def neighbors(pos: Position, width: int, height: int):
    x, y = pos
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            yield (nx, ny)

def a_star(start: Position, goal: Position, width: int, height: int) -> List[Position]:
    if start == goal:
        return []
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from: Dict[Position, Optional[Position]] = {start: None}
    cost_so_far: Dict[Position, int] = {start: 0}
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
        for n in neighbors(current, width, height):
            new_cost = cost_so_far[current] + 1
            if n not in cost_so_far or new_cost < cost_so_far[n]:
                cost_so_far[n] = new_cost
                priority = new_cost + heuristic(n, goal)
                heapq.heappush(frontier, (priority, n))
                came_from[n] = current
    if goal not in came_from:
        return []
    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path