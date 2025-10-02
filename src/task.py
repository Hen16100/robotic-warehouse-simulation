from dataclasses import dataclass
from typing import Tuple, Optional

Position = Tuple[int, int]

@dataclass
class Task:
    id: int
    order_id: Optional[int]
    shelf_id: Optional[int]
    pickup: Optional[Position] = None
    dropoff: Optional[Position] = None
    item: Optional[str] = None
    qty: int = 1
    status: str = "unassigned"
