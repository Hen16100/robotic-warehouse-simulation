from typing import Tuple, List, Optional
from dataclasses import dataclass, field
from task import Task

Position = Tuple[int, int]

@dataclass
class Robot:
    id: int
    pos: Position
    carrying_task: Optional[int] = None
    path: List[Position] = field(default_factory=list)
    state: str = "idle"

    def step(self):
        if self.path:
            self.pos = self.path.pop(0)
            if not self.path:
                if self.state == 'to_pickup':
                    self.state = 'to_dropoff'
                elif self.state == 'to_dropoff':
                    self.state = 'idle'
                    self.carrying_task = None
        return self.pos

    def assign_task(self, task: Task, path_to_pickup: List[Position], path_to_dropoff: List[Position]):
        self.carrying_task = task.id
        self.path = path_to_pickup + path_to_dropoff
        self.state = 'to_pickup'
