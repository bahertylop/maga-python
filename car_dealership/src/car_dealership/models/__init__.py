"""
Экспорт всех моделей проекта.

Позволяет импортировать всё напрямую:

    from src.car_dealership.models import Car, Sedan, Motorcycle
"""

from .engine import Engine
from .vehicle_item import VehicleItem
from .car import Car
from .sedan import Sedan
from .suv import SUV
from .motorcycle import Motorcycle
from .electric_car import ElectricCar
from .client import Client, Manager

# Имя класса -> класс. Нужен базе данных, чтобы восстановить
# правильный тип объекта из строки таблицы.
VEHICLE_TYPES = {
    cls.__name__: cls
    for cls in (Car, Sedan, SUV, Motorcycle, ElectricCar)
}

__all__ = [
    "Engine",
    "VehicleItem",
    "Car",
    "Sedan",
    "SUV",
    "Motorcycle",
    "ElectricCar",
    "Client",
    "Manager",
    "VEHICLE_TYPES",
]
