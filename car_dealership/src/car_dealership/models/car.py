"""
Автомобиль.

Главная модель проекта. Демонстрирует:
- @dataclass и наследование от dataclass (глава 20)
- миксин LoggableMixin (глава 20)
- интерфейсы Sellable, Rentable, Serviceable (глава 40)
- классовый счётчик count (глава 16)
- __post_init__ (глава 20), property (глава 14)
- композицию с Engine (глава 8)
- копирование через dataclasses.replace (глава 29)
- классовый метод from_dict (глава 15)
"""

from dataclasses import dataclass, replace
from typing import Optional

from ..interfaces import Sellable, Rentable, Serviceable
from ..utils import CarUtils
from .engine import Engine
from .vehicle_item import VehicleItem


@dataclass
class Car(VehicleItem, Sellable, Rentable, Serviceable):
    """Автомобиль: продаётся, выдаётся в прокат, обслуживается."""

    engine: Optional[Engine] = None

    # Пробег, после которого требуется плановое ТО.
    SERVICE_INTERVAL = 15_000

    def get_info(self) -> str:
        """Возвращает текстовое описание автомобиля."""
        text = (
            f"{self.title} ({self.year}), VIN {self.vin}: "
            f"{CarUtils.format_mileage(self.mileage)}, "
            f"{CarUtils.format_price(self.price)}"
        )
        if self.engine is not None:
            text += f", {self.engine.show()}"
        return text

    def sell(self) -> str:
        """Продаёт автомобиль."""
        return self._mark_sold()

    def rent(self) -> str:
        """Выдаёт автомобиль в прокат."""
        return "Выдан в прокат"

    def service(self) -> str:
        """Проводит плановое ТО."""
        return f"ТО выполнено: {self.title}, пробег {self.mileage} км"

    @property
    def needs_service(self) -> bool:
        """Нужно ли ТО: пробег достиг межсервисного интервала."""
        return self.mileage >= self.SERVICE_INTERVAL

    def insurance_cost(self) -> int:
        """Стоимость страховки для обычного автомобиля."""
        return 45_000

    def clone(self, **changes) -> "Car":
        """Копия автомобиля с изменёнными полями (глава 29)."""
        return replace(self, **changes)

    @classmethod
    def _convert(cls, kwargs: dict) -> dict:
        """Превращает вложенный словарь двигателя в объект Engine."""
        if isinstance(kwargs.get("engine"), dict):
            kwargs["engine"] = Engine.from_dict(kwargs["engine"])
        return kwargs
