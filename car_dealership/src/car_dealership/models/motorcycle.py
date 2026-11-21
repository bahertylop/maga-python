"""
Мотоцикл.

Отдельный тип транспорта (не автомобиль): продаётся, но в прокат
через наш салон не выдаётся. Демонстрирует:
- наследование от VehicleItem (глава 3)
- выборочную реализацию интерфейсов: только Sellable (глава 40)
- @dataclass (глава 20)
"""

from dataclasses import dataclass

from ..interfaces import Sellable
from ..utils import CarUtils
from .vehicle_item import VehicleItem


@dataclass
class Motorcycle(VehicleItem, Sellable):
    """Мотоцикл. Интерфейс Rentable не реализует."""

    engine_cc: int = 600

    def get_info(self) -> str:
        """Описание мотоцикла."""
        return (
            f"Мотоцикл {self.title} ({self.year}), VIN {self.vin}: "
            f"{self.engine_cc} см³, {CarUtils.format_price(self.price)}"
        )

    def sell(self) -> str:
        """Продаёт мотоцикл."""
        return self._mark_sold("Мотоцикл продан")

    def insurance_cost(self) -> int:
        """Стоимость страховки для мотоцикла."""
        return 15_000
