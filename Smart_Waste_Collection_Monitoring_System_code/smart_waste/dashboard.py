"""Tkinter dashboard for live monitoring of the waste bin network.

Run this module directly (``python -m smart_waste.dashboard``) to launch
the GUI. It requires a desktop environment with Tk available (Tk ships
with the standard python.org installers; on some Linux distributions you
may need to install it separately, e.g. ``sudo apt install python3-tk``).
"""

from datetime import datetime
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .analyzer import CollectionAnalyzer
from .database import WasteDatabase
from .models import Bin
from .route_optimizer import RouteOptimizer
from .sensor_simulator import SensorSimulator

STATUS_COLORS = {"NORMAL": "#1FA774", "WARNING": "#E9A23B", "CRITICAL": "#E15554"}


class Dashboard(tk.Tk):
    def __init__(self, bins, db: WasteDatabase, depot=(0.0, 0.0)):
        super().__init__()
        self.title("Smart Waste Collection Monitoring System")
        self.geometry("1000x650")

        self.bins = {b.bin_id: b for b in bins}
        self.db = db
        self.simulator = SensorSimulator(list(self.bins.values()))
        self.analyzer = CollectionAnalyzer()
        self.optimizer = RouteOptimizer(depot=depot)

        self._build_layout()
        self.refresh()

    # ---------------------------------------------------------------- UI --
    def _build_layout(self) -> None:
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Button(top, text="Refresh (next reading cycle)", command=self.refresh).pack(side="left")
        self.summary_var = tk.StringVar()
        ttk.Label(top, textvariable=self.summary_var, font=("Segoe UI", 11, "bold")).pack(side="left", padx=20)

        body = ttk.Frame(self, padding=10)
        body.pack(fill="both", expand=True)

        # --- Left: bin status table ---
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)
        columns = ("bin_id", "fill_pct", "status")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        for col, label in zip(columns, ("Bin ID", "Fill %", "Status")):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select_bin)

        # --- Right: chart + route ---
        right = ttk.Frame(body, width=420)
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.figure = Figure(figsize=(4.2, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        ttk.Label(right, text="Recommended Collection Route", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", pady=(10, 0)
        )
        self.route_var = tk.StringVar(value="No bins currently need collection.")
        ttk.Label(right, textvariable=self.route_var, wraplength=400, justify="left").pack(anchor="w")

    # ----------------------------------------------------------- actions --
    def refresh(self) -> None:
        readings = self.simulator.step(datetime.now())
        self.db.insert_readings(readings)

        self.tree.delete(*self.tree.get_children())
        for b in sorted(self.bins.values(), key=lambda x: x.bin_id):
            status = b.status(self.analyzer.warning, self.analyzer.critical)
            self.tree.insert("", "end", iid=str(b.bin_id), values=(b.bin_id, f"{b.fill_pct:.1f}", status))

        summary = self.analyzer.summarize(list(self.bins.values()))
        self.summary_var.set(
            f"Normal: {summary['NORMAL']}   Warning: {summary['WARNING']}   Critical: {summary['CRITICAL']}"
        )

        flagged = self.analyzer.bins_needing_collection(list(self.bins.values()))
        route = self.optimizer.optimize(flagged)
        if route:
            order = " -> ".join(f"Bin {b.bin_id}" for b in route)
            dist = self.optimizer.total_distance(route)
            self.route_var.set(f"Depot -> {order} -> Depot\nTotal distance: {dist:.1f} units")
        else:
            self.route_var.set("No bins currently need collection.")

        if self.tree.selection():
            self._plot_history(int(self.tree.selection()[0]))
        elif self.bins:
            first_id = sorted(self.bins.keys())[0]
            self.tree.selection_set(str(first_id))
            self._plot_history(first_id)

    def _on_select_bin(self, _event) -> None:
        sel = self.tree.selection()
        if sel:
            self._plot_history(int(sel[0]))

    def _plot_history(self, bin_id: int) -> None:
        history = self.db.history_for_bin(bin_id)
        self.ax.clear()
        if history:
            values = [h[0] for h in history]
            self.ax.plot(range(len(values)), values, marker="o", color="#028090")
        self.ax.set_title(f"Fill-Level Trend — Bin {bin_id}")
        self.ax.set_xlabel("Reading #")
        self.ax.set_ylabel("Fill %")
        self.ax.set_ylim(0, 105)
        self.figure.tight_layout()
        self.canvas.draw()


def make_demo_bins(n: int = 15, seed: int = 7):
    import random

    rng = random.Random(seed)
    return [Bin(bin_id=i + 1, x=rng.uniform(0, 20), y=rng.uniform(0, 20)) for i in range(n)]


if __name__ == "__main__":
    database = WasteDatabase("waste.db")
    demo_bins = make_demo_bins()
    database.insert_bins(demo_bins)
    app = Dashboard(demo_bins, database)
    app.mainloop()
    database.close()
