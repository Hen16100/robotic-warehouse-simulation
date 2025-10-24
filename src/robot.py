from typing import Tuple, List, Optional
from dataclasses import dataclass, field
from task import Task

Position = Tuple[int, int]

@dataclass
class Robot:
    id: int
    pos: Position
    carrying_task: Optional[int] = None
    path_to_pickup: List[Position] = field(default_factory=list)
    path_to_dropoff: List[Position] = field(default_factory=list)
    state: str = "idle"
    active_steps: int = 0

    def step(self, occupied_next_positions: set):
        """
        Move robot along path respecting occupied positions.
        Lower-priority robots wait if their next cell is blocked.
        """
        current_path = None
        if self.state == 'to_pickup':
            current_path = self.path_to_pickup
        elif self.state == 'to_dropoff':
            current_path = self.path_to_dropoff
        if current_path and current_path[0] not in occupied_next_positions:
            next_pos = current_path.pop(0)
            self.pos = next_pos
            self.active_steps += 1
            return next_pos
        return self.pos

    def assign_task(self, task: Task, path_to_pickup: List[Position], path_to_dropoff: List[Position]):
        self.carrying_task = task.id
        self.path_to_pickup = path_to_pickup
        self.path_to_dropoff = path_to_dropoff
        if path_to_pickup:
            self.state = 'to_pickup'
        elif path_to_dropoff:
            self.state = 'to_dropoff'
        else:
            self.state = 'idle'
