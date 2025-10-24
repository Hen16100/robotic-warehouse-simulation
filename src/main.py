from run_manager import RunManager

if __name__ == '__main__':
    manager = RunManager(
        width=18,
        height=15,
        nrobots=5,
        ntasks=8,
        steps=200,
        algo='fifo',
        seed=42
    )

    # Single run
    #csv_file, json_file = manager.run_single(run_id=1)

    # Multiple runs
    manager.run_multiple(runs = 10)

