"""Command-line entry point: runs the full simulation without the GUI.

This generates a bin network, simulates sensor readings over time, stores
everything in SQLite, evaluates alerts, computes an optimized collection
route, and prints a comparison against a naive fixed-schedule baseline
(visiting every bin in ID order regardless of fill level).

Usage:
    python main.py                # run with defaults
    python main.py --bins 20 --hours 96 --step-hours 4
    python main.py --dashboard    # also launch the Tkinter dashboard
"""

import argparse
import random

from smart_waste import Bin, SensorSimulator, WasteDatabase, CollectionAnalyzer, RouteOptimizer


def make_bins(n: int, seed: int, area: float = 20.0):
    rng = random.Random(seed)
    return [Bin(bin_id=i + 1, x=rng.uniform(0, area), y=rng.uniform(0, area)) for i in range(n)]


def run(n_bins: int, hours: int, step_hours: int, seed: int, db_path: str):
    bins = make_bins(n_bins, seed)

    db = WasteDatabase(db_path)
    db.insert_bins(bins)

    simulator = SensorSimulator(bins, seed=seed)
    readings = simulator.run(hours=hours, step_hours=step_hours)
    db.insert_readings(readings)

    analyzer = CollectionAnalyzer(warning=60, critical=80)
    optimizer = RouteOptimizer(depot=(0.0, 0.0))

    summary = analyzer.summarize(bins)
    flagged = analyzer.bins_needing_collection(bins)
    smart_route = optimizer.optimize(flagged)
    smart_distance = optimizer.total_distance(smart_route)

    # Baseline: fixed schedule visits every bin, in ID order, regardless of fill.
    baseline_route = sorted(bins, key=lambda b: b.bin_id)
    baseline_distance = optimizer.total_distance(baseline_route)

    print("=" * 60)
    print("SMART WASTE COLLECTION MONITORING SYSTEM — SIMULATION RUN")
    print("=" * 60)
    print(f"Bins simulated:        {n_bins}")
    print(f"Simulated period:      {hours}h in {step_hours}h steps "
          f"({hours // step_hours} readings/bin)")
    print(f"Readings stored in:    {db_path}")
    print()
    print("Bin status after final reading:")
    for b in bins:
        print(f"  {b!r}")
    print()
    print(f"Status summary: {summary}")
    print()
    print(f"Bins flagged for collection (>=80% full): {len(flagged)} of {n_bins}")
    if smart_route:
        order = " -> ".join(f"Bin {b.bin_id}" for b in smart_route)
        print(f"Optimized route: Depot -> {order} -> Depot")
    print()
    print("-" * 60)
    print("COMPARISON VS. FIXED-SCHEDULE BASELINE")
    print("-" * 60)
    print(f"Fixed schedule  : visits all {n_bins} bins, distance = {baseline_distance:.1f} units")
    print(f"Smart monitoring: visits {len(flagged)} bins,  distance = {smart_distance:.1f} units")
    if baseline_distance > 0:
        pct = 100 * (1 - smart_distance / baseline_distance)
        print(f"Distance reduction: {pct:.1f}%")
    print(f"Bins skipped (already had capacity): {n_bins - len(flagged)}")

    db.close()
    return bins, summary, smart_route


def parse_args():
    p = argparse.ArgumentParser(description="Smart Waste Collection Monitoring System")
    p.add_argument("--bins", type=int, default=15, help="Number of bins to simulate")
    p.add_argument("--hours", type=int, default=72, help="Total simulated hours")
    p.add_argument("--step-hours", type=int, default=4, help="Hours between sensor readings")
    p.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    p.add_argument("--db", type=str, default="waste.db", help="SQLite database file path")
    p.add_argument("--dashboard", action="store_true", help="Launch the Tkinter dashboard after the run")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result_bins, _, _ = run(args.bins, args.hours, args.step_hours, args.seed, args.db)

    if args.dashboard:
        from smart_waste.dashboard import Dashboard
        from smart_waste.database import WasteDatabase as _DB

        dash_db = _DB(args.db)
        app = Dashboard(result_bins, dash_db)
        app.mainloop()
        dash_db.close()
