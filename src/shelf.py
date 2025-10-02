from dataclasses import dataclass, field
from typing import Dict, Tuple

Position = Tuple[int, int]

@dataclass
class Shelf:
    id: int
    pos: Position
    inventory: Dict[str, int] = field(default_factory=dict)

    def has_item(self, item: str, qty: int = 1) -> bool:
        return self.inventory.get(item,0) >= qty

    def remove_item(self, item: str, qty: int = 1) -> bool:
        if self.has_item(item,qty):
            self.inventory[item] -= qty
            if self.inventory[item] == 0:
                del self.inventory[item]
            return True
        return False

    def add_item(self, item: str, qty: int = 1):
        self.inventory[item] = self.inventory.get(item, 0) + qty
