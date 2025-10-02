from typing import List, Tuple, Optional, Dict
from shelf import Shelf
from order import Order
from task import Task
import random

Position = Tuple[int, int]

class Warehouse:
    def __init__(self, width: int, height: int, seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.shelves: Dict[str, Shelf] = {}
        self.orders: Dict[int, Order] = {}
        self.tasks: List[Task] = []
        if seed is not None:
            random.seed(seed)
        self._next_task_id = 1
        self._next_shelf_id = 1
        self._next_order_id = 1

    def add_shelf(self, pos: Position, inventory: Optional[Dict[str, int]] = None) -> int:
        sid = self._next_shelf_id
        self._next_shelf_id += 1
        shelf = Shelf(sid, pos, inventory or {})
        self.shelves[sid] = shelf
        return sid

    def get_shelf(self, shelf_id: int) -> Optional[Shelf]:
        return self.shelves.get(shelf_id)

    def add_order(self, items: Dict[str, int], destination: Position) -> int:
        oid = self._next_order_id
        self._next_order_id += 1
        order = Order(oid, items, destination)
        self.orders[oid] = order
        for item, qty in items.items():
            for _ in range(qty):
                shelf_id = self._find_shelf_with_item(item)
                if shelf_id is None:
                    continue
                self.add_task(order_id = oid, shelf_id = shelf_id, item = item, qty = 1, pickup = self.shelves[shelf_id].pos, dropoff = destination)
        return oid

    def _find_shelf_with_item(self, item: str) -> Optional[int]:
        for sid, shelf in self.shelves.items():
            if shelf.has_item(item):
                return sid
        return None

    def add_task(self, order_id: Optional[int], shelf_id: Optional[int], item: Optional[str], qty: int = 1, pickup: Optional[Position] = None, dropoff: Optional[Position] = None) -> int:
        tid = self._next_task_id
        self._next_task_id += 1
        task = Task(tid, order_id, shelf_id, pickup, dropoff, item, qty, status = 'unassigned')
        self.tasks.append(task)
        return tid

    def list_unassigned(self) -> List[Task]:
        return [t for t in self.tasks if t.status == 'unassigned']

    def pop_task(self, task_id: Optional[int] = None) -> Optional[Task]:
        if task_id is None:
            if self.tasks:
                return self.tasks.pop(0)
            return None
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                return self.tasks.pop(i)
        return None

    def mark_task_completed(self, task_id: int):
        for t in self.tasks:
            if t.id == task_id:
                t.status = 'completed'
                if t.shelf_id:
                    shelf = self.get_shelf(t.shelf_id)
                    if shelf:
                        shelf.remove_item(t.item, t.qty)
                if t.order_id:
                    if all(ts.status == 'completed' for ts in self.tasks if ts.order_id == t.order_id):
                        if t.order_id in self.orders:
                            self.orders[t.order_id].status = 'completed'
                return

    def seed_shelves(self, n: int):
        for i in range(n):
            pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            inv = {'itemA': random.randint(1, 5), 'itemB': random.randint(0, 3)}
            self.add_shelf(pos, inv)

    def random_tasks(self, n: int):
        for i in range(n):
            p = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            d = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            self.add_task(order_id = None, shelf_id = None, item = None, qty = 1, pickup = p, dropoff = d)