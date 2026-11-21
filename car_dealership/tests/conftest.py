"""
Общие фикстуры для тестов.

pytest находит этот файл автоматически. Фикстуры доступны
во всех тестах без импорта.
"""

import pytest

from src.car_dealership.models import Car, Motorcycle
from src.car_dealership.services import CarStorage
from tests.vins import VIN_1, VIN_3


@pytest.fixture
def sample_car():
    """Свежий автомобиль для теста."""
    return Car(VIN_1, "Toyota", "Camry", 3_000_000, 2023, 15_000)


@pytest.fixture
def sample_motorcycle():
    """Свежий мотоцикл для теста."""
    return Motorcycle(VIN_3, "BMW", "R1250", 1_900_000)


@pytest.fixture
def sample_storage():
    """Пустое хранилище для теста."""
    return CarStorage()


@pytest.fixture
def sample_db_path(tmp_path):
    """Временный путь к базе данных."""
    return str(tmp_path / "test.db")
