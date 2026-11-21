"""
Седан.

Наследник Car. Демонстрирует:
- наследование (глава 3)
- переопределение метода (глава 9)
- @dataclass с дополнительным полем (глава 20)
"""

from dataclasses import dataclass

from ..utils import CarUtils
from .car import Car


@dataclass
class Sedan(Car):
    """Седан — автомобиль с отдельным багажником."""

    trunk_volume: int = 500

    def get_info(self) -> str:
        """Переопределённое описание для седана."""
        return (
            f"Седан {self.title} ({self.year}), VIN {self.vin}: "
            f"багажник {self.trunk_volume} л, "
            f"{CarUtils.format_price(self.price)}"
        )

    def insurance_cost(self) -> int:
        """Стоимость страховки для седана."""
        return 40_000
