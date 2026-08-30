"""Smart Waste Collection Monitoring System.

A Python simulation of an IoT-style smart-bin network: sensor simulation,
SQLite persistence, threshold-based alerting, nearest-neighbour route
optimization, and a Tkinter dashboard.
"""

from .models import Bin
from .sensor_simulator import SensorSimulator
from .database import WasteDatabase
from .analyzer import CollectionAnalyzer
from .route_optimizer import RouteOptimizer

__all__ = [
    "Bin",
    "SensorSimulator",
    "WasteDatabase",
    "CollectionAnalyzer",
    "RouteOptimizer",
]
