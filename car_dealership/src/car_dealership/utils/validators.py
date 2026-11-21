"""
Статические утилиты для проверки и форматирования данных.

Класс не имеет состояния. Все методы — статические.
Вызываются напрямую через имя класса:

    CarUtils.is_valid_vin("XTA210930Y2765432")
"""

import re

_VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


class CarUtils:
    """
    Утилиты для проверки корректности данных об автомобилях.

    Все методы — статические. Объект класса создавать не нужно.
    """

    MIN_YEAR = 1950
    MAX_YEAR = 2100
    MAX_MILEAGE = 1_000_000

    @staticmethod
    def is_valid_vin(vin) -> bool:
        """
        Проверяет VIN: 17 символов, латинские заглавные буквы и цифры,
        буквы I, O, Q не допускаются (их легко спутать с 1 и 0).
        """
        return isinstance(vin, str) and bool(_VIN_PATTERN.match(vin))

    @staticmethod
    def is_valid_price(price) -> bool:
        """Цена должна быть положительным числом (bool не считается числом)."""
        return (
            isinstance(price, (int, float))
            and not isinstance(price, bool)
            and price > 0
        )

    @staticmethod
    def is_valid_year(year) -> bool:
        """Год выпуска должен быть целым числом от 1950 до 2100."""
        return (
            isinstance(year, int)
            and not isinstance(year, bool)
            and CarUtils.MIN_YEAR <= year <= CarUtils.MAX_YEAR
        )

    @staticmethod
    def is_valid_mileage(mileage) -> bool:
        """Пробег — целое число от 0 до 1 000 000 км."""
        return (
            isinstance(mileage, int)
            and not isinstance(mileage, bool)
            and 0 <= mileage <= CarUtils.MAX_MILEAGE
        )

    @staticmethod
    def format_price(price) -> str:
        """Форматирует цену с пробелами-разделителями: 3 000 000 ₽."""
        return f"{price:,.0f} ₽".replace(",", " ")

    @staticmethod
    def format_mileage(mileage) -> str:
        """Форматирует пробег: 15 000 км."""
        return f"{mileage:,} км".replace(",", " ")
