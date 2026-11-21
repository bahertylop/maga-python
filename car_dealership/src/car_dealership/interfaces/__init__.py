"""
Экспорт интерфейсов и миксинов.

Позволяет импортировать всё напрямую из пакета interfaces:

    from src.car_dealership.interfaces import Infoable, Notifier
"""

from .protocols import (
    Infoable,
    Sellable,
    Rentable,
    Serviceable,
    Describable,
    Notifier,
    Storage,
)
from .mixins import LoggableMixin, TimestampMixin

__all__ = [
    "Infoable",
    "Sellable",
    "Rentable",
    "Serviceable",
    "Describable",
    "Notifier",
    "Storage",
    "LoggableMixin",
    "TimestampMixin",
]
