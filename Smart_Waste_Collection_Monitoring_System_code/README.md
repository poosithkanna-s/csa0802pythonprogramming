# Smart Waste Collection Monitoring System

Python implementation accompanying the capstone report. Simulates a network
of waste bins, stores fill-level history in SQLite, raises threshold-based
alerts, computes an optimized collection route, and (optionally) displays
everything in a Tkinter dashboard.

## Project layout

```
smart_waste/
    __init__.py
    models.py            # Bin dataclass
    sensor_simulator.py  # SensorSimulator
    database.py          # WasteDatabase (SQLite)
    analyzer.py          # CollectionAnalyzer (thresholds/alerts)
    route_optimizer.py   # RouteOptimizer (nearest-neighbour)
    dashboard.py          # Tkinter + Matplotlib dashboard
main.py                  # headless CLI runner
tests/
    test_smart_waste.py  # unit tests
requirements.txt
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`sqlite3` and `tkinter` are part of the Python standard library.
If `tkinter` is missing on Linux: `sudo apt install python3-tk`.

## Run the simulation (no GUI required)

```bash
python main.py
python main.py --bins 20 --hours 96 --step-hours 4
```

This prints each bin's final status, the alert summary, the optimized
route, and a comparison against a fixed-schedule baseline.

## Run with the live dashboard

```bash
python main.py --dashboard
# or directly:
python -m smart_waste.dashboard
```

Requires a desktop environment (Tk needs a display).

## Run the tests

```bash
python -m unittest discover tests -v
```
