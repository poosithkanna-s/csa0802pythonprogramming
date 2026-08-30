"""Simulates ultrasonic fill-level sensors for a network of bins."""

import random
from datetime import datetime, timedelta
from typing import List, Tuple

from .models import Bin

# A reading is (bin_id, fill_pct, iso_timestamp)
Reading = Tuple[int, float, str]


class SensorSimulator:
    """Generates realistic, time-stamped fill-level readings for a set of bins.

    Fill levels rise gradually each cycle. To mimic a bin having already been
    collected off-schedule (or simply to keep the simulation varied), a bin
    has a small chance of resetting to a low fill level on any given step.
    """

    def __init__(self, bins: List[Bin], seed: int = 42, reset_chance: float = 0.04):
        self.bins = bins
        self.rng = random.Random(seed)
        self.reset_chance = reset_chance

    def step(self, current_time: datetime) -> List[Reading]:
        """Advance every bin by one reading and return the new readings."""
        readings: List[Reading] = []
        for b in self.bins:
            if self.rng.random() < self.reset_chance:
                b.fill_pct = self.rng.uniform(0.0, 8.0)  # bin was emptied
            else:
                increment = self.rng.uniform(2.0, 9.0)
                b.fill_pct = min(100.0, b.fill_pct + increment)
            readings.append((b.bin_id, round(b.fill_pct, 2), current_time.isoformat()))
        return readings

    def run(self, hours: int = 72, step_hours: int = 4) -> List[Reading]:
        """Run the simulation for a number of hours, at a fixed step interval.

        Returns the full list of readings generated across every bin and
        every time step, suitable for bulk insertion into the database.
        """
        start = datetime.now()
        all_readings: List[Reading] = []
        for i in range(hours // step_hours):
            t = start + timedelta(hours=i * step_hours)
            all_readings.extend(self.step(t))
        return all_readings
