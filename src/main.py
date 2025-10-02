import argparse
import csv
from warehouse import Warehouse
from robot import Robot
from scheduler import fifo_allocate, nearest_allocate

def run_sim(width = 8, height = 6, nrobots = 2, ntasks = 6, algo = 'fifo', steps = 200, seed = 42, out = 'sample_run.csv'):
    wh = Warehouse(width, height, seed = seed)
    wh.seed_shelves(6)
    for i in range(ntasks):
        wh.add_order({'itemA': 1}, destination = (width - 1, height - 1))

    robots = [Robot(id = i + 1, pos = (0, i)) for i in range(nrobots)]
    alloc = fifo_allocate if algo == 'fifo' else nearest_allocate

    rows = []
    for t in range(steps):
        allocated = alloc(wh, robots, width, height)
        for r in robots:
            prev = r.pos
            r.step()
            rows.append({'time': t, 'robot': r.id, 'pos': r.pos, 'state': r.state, 'carrying_task': r.carrying_task})
        if not wh.tasks and all(r.state == 'idle' for r in robots):
            break
    with open(out, 'w', newline = '') as f:
        writer = csv.DictWriter(f, fieldnames = ['time', 'robot', 'pos', 'state', 'carrying_task'])
        writer.writeheader()
        for r in rows:
            writer.writerow({'time': r['time'], 'robot': r['robot'], 'pos': f"{r['pos']}", 'state': r['state'], 'carrying_task': r['carrying_task']})
    print(f"Run complete. Output -> {out}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--width', type = int, default = 8)
    parser.add_argument('--height', type = int, default = 6)
    parser.add_argument('--nrobots', type = int, default = 2)
    parser.add_argument('--ntasks', type = int, default = 6)
    parser.add_argument('--algo', choices = ['fifo', 'nearest'], default = 'fifo')
    parser.add_argument('--steps', type = int, default = 200)
    parser.add_argument('--seed', type = int, default = 42)
    parser.add_argument('--out', type = str, default = 'sample_run.csv')
    args = parser.parse_args()
    run_sim(args.width, args.height, args.nrobots, args.ntasks, args.algo, args.steps, args.seed, args.out)

