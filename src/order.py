from dataclasses import dataclass
from typing import Dict, Tuple

Position = Tuple[int, int]

@dataclass
class Order:
    id = int
    items: Dict[str, int]
    destination: Position
    status: str = "created"