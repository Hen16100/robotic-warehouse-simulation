import csv
import json
import random
import time
from typing import List, Dict, Tuple
from warehouse import Warehouse
from robot import Robot
from scheduler import fifo_allocate, nearest_allocate
from pathfinding import a_star
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation

Position = Tuple[int, int]

class RunManager:
    def __init__(self, width: int = 8, height: int = 6, nrobots: int = 2,
                 ntasks: int = 6, steps: int = 200, algo: str = 'fifo', seed: int = 42):
        self.width = width
        self.height = height
        self.nrobots = nrobots
        self.ntasks = ntasks
        self.steps = steps
        self.algo = algo
        self.seed = seed

    def _init_warehouse(self, seed_override=None):
        """Initialize warehouse with shelves and randomized pickup but fixed dropoff."""
        seed_value = seed_override or self.seed
        random.seed(seed_value)
        warehouse = Warehouse(self.width, self.height, seed=seed_value)
        warehouse.seed_shelves(15)
        shelf_positions = [s.pos for s in warehouse.shelves.values()]
        dropoff = (self.width - 1, self.height - 1)
        for _ in range(self.ntasks):
            pickup = random.choice(shelf_positions)
            warehouse.add_task(
                order_id=None,
                shelf_id=None,
                item='itemA',
                qty=1,
                pickup=pickup,
                dropoff=dropoff
            )
        return warehouse

    def _init_robots(self, warehouse: Warehouse):
        """Spawn robots at random, non-shelf positions."""
        shelf_positions = {s.pos for s in warehouse.shelves.values()}
        robots = []
        occupied = set(shelf_positions)
        for i in range(self.nrobots):
            while True:
                pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
                if pos not in occupied:
                    robots.append(Robot(id=i + 1, pos=pos))
                    occupied.add(pos)
                    break
        return robots

    def run_single(self, run_id: int = 1) -> Tuple[str, str]:
        # Unique seed per run for varied simulations
        random.seed(self.seed + run_id)
        warehouse = self._init_warehouse(seed_override=self.seed + run_id)
        robots = self._init_robots(warehouse)
        alloc = fifo_allocate if self.algo == 'fifo' else nearest_allocate
        rows = []
        robot_utilization = {r.id: 0 for r in robots}
        start_time = time.time()
        for t in range(self.steps):
            assigned = alloc(warehouse, robots, self.width, self.height)
            reserved_positions = set()
            for r in sorted(robots, key=lambda r: r.id):
                r.step(occupied_next_positions=reserved_positions)
                if r.state in ('to_pickup', 'to_dropoff') and r.pos:
                    reserved_positions.add(r.pos)
                if r.state != 'idle':
                    robot_utilization[r.id] += 1
                rows.append({
                    'time': t,
                    'robot': r.id,
                    'pos': r.pos,
                    'state': r.state,
                    'carrying_task': r.carrying_task
                })
            if not warehouse.tasks and all(r.state == 'idle' for r in robots):
                break
        duration = time.time() - start_time
        duration_rounded = round(duration, 5)
        csv_file = f'run_{run_id:03d}.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['time', 'robot', 'pos', 'state', 'carrying_task'])
            writer.writeheader()
            writer.writerows(rows)
        json_file = f'run_{run_id:03d}_summary.json'
        summary = {
            'run_id': run_id,
            'steps': t + 1,
            'duration_s': duration_rounded,
            'nrobots': self.nrobots,
            'ntasks': self.ntasks,
            'robot_utilization': robot_utilization
        }
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2)
        self._animate_run(warehouse, robots, run_id, rows)
        print(f"Run {run_id} complete. CSV -> {csv_file}, JSON -> {json_file}")
        return csv_file, json_file

    def _animate_run(self, warehouse: Warehouse, robots: List[Robot], run_id: int, rows: List[Dict]):
        fig, ax = plt.subplots()
        ax.set_xlim(-1, self.width)
        ax.set_ylim(-1, self.height)
        ax.set_aspect('equal')
        ax.set_title(f"Warehouse Simulation Run {run_id}")
        for s in warehouse.shelves.values():
            ax.add_patch(Rectangle((s.pos[0]-0.4, s.pos[1]-0.4), 0.8, 0.8, color='saddlebrown'))
        ax.add_patch(Rectangle((self.width - 1 - 0.4, self.height - 1 - 0.4),
                               0.8, 0.8, color='green', alpha=0.4))
        robot_positions = {r.id: [] for r in robots}
        max_time = max(row['time'] for row in rows) + 1
        for rid in robot_positions.keys():
            for t in range(max_time):
                row = next((row for row in rows if row['time'] == t and row['robot'] == rid), None)
                if row:
                    robot_positions[rid].append(row['pos'])
                else:
                    robot_positions[rid].append(robot_positions[rid][-1] if robot_positions[rid] else (0, 0))
        colors = plt.cm.get_cmap('tab10', len(robots))
        dots = [ax.plot([], [], 'o', c=colors(i), label=f'Robot {r.id}')[0] for i, r in enumerate(robots)]
        ax.legend(loc='upper left')

        def update(frame):
            for i, rid in enumerate(robot_positions.keys()):
                x, y = robot_positions[rid][frame]
                dots[i].set_data([x], [y])
            return dots
        ani = FuncAnimation(fig, update, frames=max_time, blit=True, repeat=False)
        gif_file = f'run_{run_id:03d}.gif'
        ani.save(gif_file, writer='pillow', fps=5)
        plt.close(fig)

    def run_multiple(self, runs: int = 10):
        """
        Runs multiple simulations with varying parameters for analysis.
        The first few runs vary grid size, robot count, and algorithm.
        The remaining runs vary only the random seed for stochastic variety.
        """
        configs = [
            (8, 6, 2, 6, 'fifo', "Baseline"),
            (20, 15, 5, 10, 'fifo', "Larger Grid"),
            (10, 8, 3, 8, 'nearest', "Nearest Algo"),
            (12, 10, 4, 6, 'fifo', "Shelf Density Test"),
        ]
        csv_files, json_files = [], []
        summary_rows = []
        for i in range(1, runs + 1):
            # Select config: first 4 are fixed tests, rest are random variations
            if i <= len(configs):
                w, h, nr, nt, algo, label = configs[i - 1]
            else:
                w = random.choice([8, 10, 12, 15, 18])
                h = random.choice([6, 8, 10, 12, 15])
                nr = random.choice([2, 3, 4, 5])
                nt = random.choice([5, 6, 8, 10])
                algo = random.choice(['fifo', 'nearest'])
                label = "Randomized"
            self.width, self.height, self.nrobots, self.ntasks, self.algo = w, h, nr, nt, algo
            csv_file, json_file = self.run_single(run_id=i)
            csv_files.append(csv_file)
            json_files.append(json_file)
            with open(json_file) as f:
                data = json.load(f)
            summary_rows.append({
                'Run ID': f"{i:03d}",
                'Purpose': label,
                'Parameters': f"{w}x{h}, {nr} robots, {algo.upper()}",
                'Duration (s)': round(data['duration_s'], 4),
                'Steps': data['steps'],
                'Status': "Complete"
            })
        with open('summary_table.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
            writer.writeheader()
            writer.writerows(summary_rows)
        print("\n=== Simulation Summary ===")
        for row in summary_rows:
            print(f"{row['Run ID']} {row['Purpose']:<18} {row['Parameters']:<30} "
                  f"{row['Duration (s)']}s {row['Steps']} {row['Status']}")
        print("\nSummary table saved to summary_table.csv")
        return csv_files, json_files
