"""
Экспорт компонентов базы данных.

Позволяет импортировать напрямую:

    from src.car_dealership.database import DatabaseManager, CarRepository
"""

from .manager import DatabaseManager
from .repositories import (
    CarRepository,
    ClientRepository,
    DealRepository,
    row_to_vehicle,
)

__all__ = [
    "DatabaseManager",
    "CarRepository",
    "ClientRepository",
    "DealRepository",
    "row_to_vehicle",
]
