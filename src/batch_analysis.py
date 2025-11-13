import os
import sys
import json
import math
from pathlib import Path
from collections import defaultdict

proj_dir = Path.cwd()
sys.path.insert(0, str(proj_dir))

from run_manager import RunManager

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# User config
# -------------------------
RUNS_PER_CONFIG = 30   # change to 30+ if you want; set lower while testing
OUTPUT_DIR = proj_dir / "batch_runs"
OUTPUT_DIR.mkdir(exist_ok=True)

CONFIGS = [
    {"w": 8,  "h": 6,  "nr": 2, "nt": 6,  "algo": "fifo",    "label": "Baseline"},
    {"w": 20, "h": 15, "nr": 5, "nt": 10, "algo": "fifo",    "label": "Larger Grid"},
    {"w": 10, "h": 8,  "nr": 3, "nt": 8,  "algo": "nearest", "label": "Nearest Algo"},
    {"w": 12, "h": 10, "nr": 4, "nt": 6,  "algo": "fifo",    "label": "Shelf Density Test"},
]

def ci95(data):
    n = len(data)
    m = float(np.mean(data)) if n > 0 else 0.0
    s = float(np.std(data, ddof=1)) if n > 1 else 0.0
    se = s / math.sqrt(n) if n > 0 else 0.0
    return {"mean": m, "std": s, "lo": m - 1.96 * se, "hi": m + 1.96 * se, "n": n}

print(f"Running {RUNS_PER_CONFIG} runs per scenario (this may take a few minutes)...")
manager = RunManager()
if hasattr(manager, "_animate_run"):
    manager._animate_run = lambda *args, **kwargs: None
records = []
for cfg_idx, cfg in enumerate(CONFIGS, start=1):
    label = cfg["label"]
    print(f"\n=== Scenario: {label} ===")
    for r in range(RUNS_PER_CONFIG):
        manager.width = cfg["w"]
        manager.height = cfg["h"]
        manager.nrobots = cfg["nr"]
        manager.ntasks = cfg["nt"]
        manager.algo = cfg["algo"]
        run_id = cfg_idx * 10_000 + r
        csv_file, json_file = manager.run_single(run_id=run_id)
        with open(json_file) as f:
            summary = json.load(f)
        ru_dict = summary.get("robot_utilization", {})
        steps = summary.get("steps", 1)
        mean_util = sum(ru_dict.values()) / (len(ru_dict) * steps) if ru_dict and len(ru_dict) > 0 else 0.0
        approx_remaining = cfg["nt"]
        try:
            import csv as _csv
            carrying = set()
            with open(csv_file, newline='') as cf:
                reader = _csv.DictReader(cf)
                for row in reader:
                    v = row.get("carrying_task")
                    if v and v != "None":
                        carrying.add(v)
            approx_completed = len(carrying)
            approx_remaining = max(0, cfg["nt"] - approx_completed)
        except Exception:
            pass
        records.append({
            "scenario": label,
            "w": cfg["w"],
            "h": cfg["h"],
            "nrobots": cfg["nr"],
            "ntasks": cfg["nt"],
            "algo": cfg["algo"],
            "run": r,
            "duration_s": summary.get("duration_s", 0.0),
            "steps": summary.get("steps", 0),
            "mean_util_frac": mean_util,
            "approx_remaining_tasks": approx_remaining,
            "csv_file": csv_file,
            "json_file": json_file
        })

# -------------------------
# Summaries and plots
# -------------------------
df = pd.DataFrame(records)
df.to_csv(OUTPUT_DIR / "all_runs.csv", index=False)
print(f"\nSaved all_runs.csv -> {OUTPUT_DIR/'all_runs.csv'}")
summary_stats = {}
for scenario, group in df.groupby("scenario"):
    durations = group["duration_s"].tolist()
    steps = group["steps"].tolist()
    utils = group["mean_util_frac"].tolist()
    summary_stats[scenario] = {
        "duration": ci95(durations),
        "steps": ci95(steps),
        "util": ci95(utils)
    }
with open(OUTPUT_DIR / "stats_summary.json", "w") as f:
    json.dump(summary_stats, f, indent=2)
print(f"Saved stats_summary.json -> {OUTPUT_DIR/'stats_summary.json'}")
baseline = summary_stats["Baseline"]
sens = {}
for cfg in CONFIGS[1:]:
    name = cfg["label"]
    cur = summary_stats[name]
    area_base = CONFIGS[0]["w"] * CONFIGS[0]["h"]
    area_cfg = cfg["w"] * cfg["h"]
    pct_area = (area_cfg - area_base) / area_base if area_base != 0 else float("inf")
    pct_nrobots = (cfg["nr"] - CONFIGS[0]["nr"]) / CONFIGS[0]["nr"]
    pct_ntasks = (cfg["nt"] - CONFIGS[0]["nt"]) / CONFIGS[0]["nt"]
    pct_duration = (cur["duration"]["mean"] - baseline["duration"]["mean"]) / baseline["duration"]["mean"] if baseline["duration"]["mean"] != 0 else float("inf")
    pct_steps = (cur["steps"]["mean"] - baseline["steps"]["mean"]) / baseline["steps"]["mean"] if baseline["steps"]["mean"] != 0 else float("inf")
    sens[name] = {
        "area_pct": pct_area,
        "nrobots_pct": pct_nrobots,
        "ntasks_pct": pct_ntasks,
        "duration_pct_change": pct_duration,
        "steps_pct_change": pct_steps,
        "duration_sensitivity_area": (pct_duration / pct_area) if pct_area != 0 else None,
        "duration_sensitivity_nrobots": (pct_duration / pct_nrobots) if pct_nrobots != 0 else None,
        "duration_sensitivity_ntasks": (pct_duration / pct_ntasks) if pct_ntasks != 0 else None
    }
with open(OUTPUT_DIR / "sensitivity.json", "w") as f:
    json.dump(sens, f, indent=2)
print(f"Saved sensitivity.json -> {OUTPUT_DIR/'sensitivity.json'}")
plt.figure(figsize=(8,4))
order = df["scenario"].unique()
for scenario in order:
    g = df[df["scenario"] == scenario]
    plt.plot(g["run"], g["duration_s"], "o-", alpha=0.6, label=scenario)
plt.title("Run Durations (per-run points) by Scenario")
plt.xlabel("run index")
plt.ylabel("duration (s)")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "durations_by_scenario.png")
plt.close()
plt.figure(figsize=(8,4))
for scenario in order:
    g = df[df["scenario"] == scenario]
    plt.plot(g["run"], g["steps"], "o-", alpha=0.6, label=scenario)
plt.title("Steps (per-run points) by Scenario")
plt.xlabel("run index")
plt.ylabel("steps")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "steps_by_scenario.png")
plt.close()
plt.figure(figsize=(8,4))
for scenario in order:
    g = df[df["scenario"] == scenario]
    plt.plot(g["run"], g["mean_util_frac"], "o-", alpha=0.6, label=scenario)
plt.title("Mean robot utilization fraction by scenario")
plt.xlabel("run index")
plt.ylabel("mean utilization fraction")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "util_by_scenario.png")
plt.close()

print("Saved plots in:", OUTPUT_DIR)