"""
Внедорожник (кроссовер).

Наследник Car. Демонстрирует:
- полиморфизм (глава 4)
- разные наследники с общим родителем
"""

from dataclasses import dataclass

from ..utils import CarUtils
from .car import Car


@dataclass
class SUV(Car):
    """Внедорожник: у него есть тип привода."""

    drive: str = "4WD"

    def get_info(self) -> str:
        """Переопределённое описание для внедорожника."""
        return (
            f"Внедорожник {self.title} ({self.year}), VIN {self.vin}: "
            f"привод {self.drive}, {CarUtils.format_price(self.price)}"
        )

    def insurance_cost(self) -> int:
        """Стоимость страховки для внедорожника."""
        return 65_000
