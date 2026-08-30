"""Data models for the Smart Waste Collection Monitoring System."""

from dataclasses import dataclass


@dataclass
class Bin:
    """Represents a single waste bin in the monitored zone."""

    bin_id: int
    x: float
    y: float
    capacity_l: int = 240
    fill_pct: float = 0.0

    def status(self, warning: float = 60, critical: float = 80) -> str:
        """Classify the bin's current fill level.

        Args:
            warning: Fill percentage at/above which the bin is "WARNING".
            critical: Fill percentage at/above which the bin is "CRITICAL".

        Returns:
            One of "NORMAL", "WARNING", "CRITICAL".
        """
        if self.fill_pct >= critical:
            return "CRITICAL"
        elif self.fill_pct >= warning:
            return "WARNING"
        return "NORMAL"

    def __repr__(self) -> str:
        return (
            f"Bin(id={self.bin_id}, pos=({self.x:.1f},{self.y:.1f}), "
            f"fill={self.fill_pct:.1f}%, status={self.status()})"
        )
