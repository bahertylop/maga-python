"""
Декораторы для меток транспортных средств.

Паттерн Decorator (глава 38). Позволяет добавлять метки
к объекту без изменения его класса. Декораторы
комбинируются в цепочку.
"""

from ..interfaces import Infoable


class ItemDecorator(Infoable):
    """
    Базовый декоратор.

    Содержит обёрнутый объект и делегирует ему вызов
    get_info(). Наследники дополняют результат.
    """

    def __init__(self, item: Infoable):
        self.item = item

    def get_info(self) -> str:
        """Делегирует работу обёрнутому объекту."""
        return self.item.get_info()


class WarrantyDecorator(ItemDecorator):
    """Добавляет метку «гарантия»."""

    def __init__(self, item: Infoable, years: int = 3):
        super().__init__(item)
        self.years = years

    def get_info(self) -> str:
        return f"{self.item.get_info()} (гарантия {self.years} г.)"


class CreditDecorator(ItemDecorator):
    """Добавляет метку «кредит возможен»."""

    def get_info(self) -> str:
        return f"{self.item.get_info()} (кредит возможен)"


class WinterTiresDecorator(ItemDecorator):
    """Добавляет метку «комплект зимней резины»."""

    def get_info(self) -> str:
        return f"{self.item.get_info()} (зимняя резина в подарок)"
