"""Nearest-neighbour route optimization for bins flagged for collection."""

import math
from typing import List, Tuple

from .models import Bin


class RouteOptimizer:
    """Computes a collection route using a nearest-neighbour heuristic.

    Starting from a fixed depot, it repeatedly travels to the closest
    unvisited flagged bin. This does not guarantee the mathematically
    optimal route (the underlying problem is the Travelling Salesman
    Problem, which is NP-hard) but gives a fast, good approximation that
    is appropriate for a municipal collection zone.
    """

    def __init__(self, depot: Tuple[float, float] = (0.0, 0.0)):
        self.depot = depot

    @staticmethod
    def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def optimize(self, bins_to_visit: List[Bin]) -> List[Bin]:
        """Return the bins reordered into an efficient visiting sequence."""
        remaining = bins_to_visit.copy()
        route: List[Bin] = []
        current = self.depot
        while remaining:
            nearest = min(remaining, key=lambda b: self._distance(current, (b.x, b.y)))
            route.append(nearest)
            current = (nearest.x, nearest.y)
            remaining.remove(nearest)
        return route

    def total_distance(self, route: List[Bin]) -> float:
        """Total travel distance for a route, starting and ending at the depot."""
        if not route:
            return 0.0
        points = [self.depot] + [(b.x, b.y) for b in route] + [self.depot]
        return sum(self._distance(points[i], points[i + 1]) for i in range(len(points) - 1))
