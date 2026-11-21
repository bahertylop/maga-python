"""
Базовый класс транспортного средства.

VehicleItem — абстрактный dataclass. Объект создать нельзя,
но любой наследник обязан реализовать get_info(). Здесь собрано
всё общее для автомобилей и мотоциклов: поля, проверка данных,
счётчик созданных объектов, сериализация.
"""

from dataclasses import dataclass, fields
from typing import ClassVar

from ..interfaces import Infoable, LoggableMixin
from ..exceptions import (
    InvalidMileageError,
    InvalidPriceError,
    InvalidVinError,
)
from ..utils import CarUtils


@dataclass
class VehicleItem(Infoable, LoggableMixin):
    """Общие данные и поведение любого транспортного средства."""

    vin: str
    brand: str
    model: str
    price: int
    year: int = 2024
    mileage: int = 0

    # Классовый счётчик: сколько транспортных средств создано всего.
    count: ClassVar[int] = 0

    def __post_init__(self) -> None:
        """Проверяет данные и задаёт служебные признаки."""
        if not CarUtils.is_valid_vin(self.vin):
            raise InvalidVinError(self.vin)
        if not CarUtils.is_valid_price(self.price):
            raise InvalidPriceError(self.price)
        if not CarUtils.is_valid_year(self.year):
            raise ValueError(
                f"Год выпуска {self.year!r} вне диапазона "
                f"[{CarUtils.MIN_YEAR}, {CarUtils.MAX_YEAR}]"
            )
        if not CarUtils.is_valid_mileage(self.mileage):
            raise InvalidMileageError(self.mileage)

        self.is_sold = False
        self.is_rented = False
        VehicleItem.count += 1

    # ─── свойства ───

    @property
    def title(self) -> str:
        """Короткое название: «Toyota Camry»."""
        return f"{self.brand} {self.model}"

    @property
    def is_new(self) -> bool:
        """Новый автомобиль — без пробега."""
        return self.mileage == 0

    def age(self, current_year: int = 2026) -> int:
        """Возраст в годах относительно указанного года."""
        return max(0, current_year - self.year)

    # ─── общая логика продажи ───

    def _mark_sold(self, message: str = "Продано") -> str:
        """Помечает объект проданным. Повторная продажа безвредна."""
        if self.is_sold:
            return "Уже продан"
        self.is_sold = True
        return message

    def insurance_cost(self) -> int:
        """Стоимость годовой страховки. Наследники уточняют сумму."""
        return 40_000

    # ─── сериализация ───

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для сохранения в БД."""
        data = {"type": type(self).__name__}
        for f in fields(self):
            value = getattr(self, f.name)
            data[f.name] = value.to_dict() if hasattr(value, "to_dict") else value
        data["is_sold"] = self.is_sold
        data["is_rented"] = self.is_rented
        return data

    @classmethod
    def _convert(cls, kwargs: dict) -> dict:
        """Хук для наследников: преобразование вложенных объектов."""
        return kwargs

    @classmethod
    def from_dict(cls, data: dict):
        """Создаёт объект из словаря при загрузке из БД."""
        names = {f.name for f in fields(cls)}
        kwargs = {
            key: value for key, value in data.items()
            if key in names and value is not None
        }
        item = cls(**cls._convert(kwargs))
        item.is_sold = bool(data.get("is_sold", False))
        item.is_rented = bool(data.get("is_rented", False))
        return item

    # ─── магические методы ───

    def describe(self) -> str:
        """Описание для утиной типизации (протокол Describable)."""
        return self.get_info()

    def __lt__(self, other) -> bool:
        """Сравнение по цене: позволяет вызывать sorted(cars)."""
        if not isinstance(other, VehicleItem):
            return NotImplemented
        return self.price < other.price

    def __str__(self) -> str:
        return self.get_info()
