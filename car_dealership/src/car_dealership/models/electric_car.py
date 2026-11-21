"""
Электромобиль.

Наследник Car. Демонстрирует:
- расширение метода через super() (глава 9)
- добавление поля в @dataclass (глава 20)
- вычисляемое свойство (глава 14)
"""

from dataclasses import dataclass

from .car import Car


@dataclass
class ElectricCar(Car):
    """Электромобиль — автомобиль с тяговой батареей."""

    battery_kwh: int = 60

    def get_info(self) -> str:
        """Дополняет родительское описание информацией о батарее."""
        parent_info = super().get_info()
        return f"{parent_info} + батарея {self.battery_kwh} кВт·ч"

    @property
    def range_km(self) -> int:
        """Приблизительный запас хода: около 6 км на каждый кВт·ч."""
        return self.battery_kwh * 6

    @property
    def needs_service(self) -> bool:
        """У электромобиля ТО нужно реже: интервал в два раза больше."""
        return self.mileage >= self.SERVICE_INTERVAL * 2

    def insurance_cost(self) -> int:
        """Стоимость страховки для электромобиля."""
        return 30_000
