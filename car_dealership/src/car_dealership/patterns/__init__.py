"""
Экспорт всех паттернов.

Позволяет импортировать напрямую:

    from src.car_dealership.patterns import CarFactory, SingletonMeta
"""

from .factory import CarFactory
from .singleton import SingletonMeta, DealershipRegistry
from .decorator import (
    ItemDecorator,
    WarrantyDecorator,
    CreditDecorator,
    WinterTiresDecorator,
)
from .adapter import CarAdapter

__all__ = [
    "CarFactory",
    "SingletonMeta",
    "DealershipRegistry",
    "ItemDecorator",
    "WarrantyDecorator",
    "CreditDecorator",
    "WinterTiresDecorator",
    "CarAdapter",
]
