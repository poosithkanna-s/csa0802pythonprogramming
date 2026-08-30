"""Threshold-based alerting and summary statistics."""

from typing import Dict, List

from .models import Bin


class CollectionAnalyzer:
    """Applies fill-level thresholds to classify bins and flag urgent ones."""

    def __init__(self, warning: float = 60, critical: float = 80):
        self.warning = warning
        self.critical = critical

    def bins_needing_collection(self, bins: List[Bin]) -> List[Bin]:
        """Return bins at or above the critical threshold."""
        return [b for b in bins if b.fill_pct >= self.critical]

    def summarize(self, bins: List[Bin]) -> Dict[str, int]:
        """Return a count of bins in each status category."""
        summary = {"NORMAL": 0, "WARNING": 0, "CRITICAL": 0}
        for b in bins:
            summary[b.status(self.warning, self.critical)] += 1
        return summary
