"""Unit tests covering the core modules (see report Chapter 6)."""

import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from smart_waste import Bin, SensorSimulator, WasteDatabase, CollectionAnalyzer, RouteOptimizer


class TestBin(unittest.TestCase):
    def test_critical_status(self):
        b = Bin(bin_id=1, x=0, y=0, fill_pct=85)
        self.assertEqual(b.status(), "CRITICAL")

    def test_warning_status(self):
        b = Bin(bin_id=2, x=0, y=0, fill_pct=65)
        self.assertEqual(b.status(), "WARNING")

    def test_normal_status(self):
        b = Bin(bin_id=3, x=0, y=0, fill_pct=20)
        self.assertEqual(b.status(), "NORMAL")


class TestSensorSimulator(unittest.TestCase):
    def test_fill_never_exceeds_100(self):
        bins = [Bin(bin_id=1, x=0, y=0, fill_pct=95)]
        sim = SensorSimulator(bins, seed=1, reset_chance=0.0)
        for _ in range(50):
            sim.step(datetime.now())
        self.assertLessEqual(bins[0].fill_pct, 100.0)

    def test_step_returns_one_reading_per_bin(self):
        bins = [Bin(bin_id=i, x=0, y=0) for i in range(1, 6)]
        sim = SensorSimulator(bins, seed=1)
        readings = sim.step(datetime.now())
        self.assertEqual(len(readings), 5)


class TestWasteDatabase(unittest.TestCase):
    def setUp(self):
        self.db = WasteDatabase(":memory:")

    def tearDown(self):
        self.db.close()

    def test_insert_and_query_bin(self):
        b = Bin(bin_id=1, x=1.5, y=2.5, capacity_l=240)
        self.db.insert_bin(b)
        row = self.db.get_bin(1)
        self.assertEqual(row, (1, 1.5, 2.5, 240))

    def test_latest_readings(self):
        self.db.insert_bin(Bin(bin_id=1, x=0, y=0))
        self.db.insert_readings([(1, 40.0, "2026-01-01T00:00:00"), (1, 55.0, "2026-01-01T04:00:00")])
        latest = self.db.latest_readings()
        self.assertEqual(latest, [(1, 55.0, "2026-01-01T04:00:00")])


class TestCollectionAnalyzer(unittest.TestCase):
    def test_bins_needing_collection_excludes_below_threshold(self):
        bins = [
            Bin(bin_id=1, x=0, y=0, fill_pct=50),
            Bin(bin_id=2, x=0, y=0, fill_pct=90),
        ]
        analyzer = CollectionAnalyzer(critical=80)
        flagged = analyzer.bins_needing_collection(bins)
        self.assertEqual([b.bin_id for b in flagged], [2])

    def test_summarize_counts_each_status(self):
        bins = [
            Bin(bin_id=1, x=0, y=0, fill_pct=10),
            Bin(bin_id=2, x=0, y=0, fill_pct=65),
            Bin(bin_id=3, x=0, y=0, fill_pct=90),
        ]
        analyzer = CollectionAnalyzer()
        summary = analyzer.summarize(bins)
        self.assertEqual(summary, {"NORMAL": 1, "WARNING": 1, "CRITICAL": 1})


class TestRouteOptimizer(unittest.TestCase):
    def test_route_visits_every_bin_exactly_once(self):
        bins = [Bin(bin_id=i, x=i, y=i, fill_pct=90) for i in range(1, 6)]
        optimizer = RouteOptimizer(depot=(0, 0))
        route = optimizer.optimize(bins)
        self.assertEqual(sorted(b.bin_id for b in route), [1, 2, 3, 4, 5])

    def test_nearest_neighbour_picks_closest_first(self):
        near = Bin(bin_id=1, x=1, y=0, fill_pct=90)
        far = Bin(bin_id=2, x=10, y=0, fill_pct=90)
        optimizer = RouteOptimizer(depot=(0, 0))
        route = optimizer.optimize([far, near])
        self.assertEqual(route[0].bin_id, 1)


if __name__ == "__main__":
    unittest.main()
